from abc import abstractmethod
import torch


class Metric:
    """Base class for all Metrics.
    """
    def __init__(self, name=None):
        self.name = self.__class__.__name__ if name is None else name
        self._sum = 0
        self._num_examples = 0
        self.stored_values = []
        self.total_updates = 0

    def reset(self):
        """Resets the metric to it's initial state.

        By default, this is called at the start of each epoch.
        """
        self._sum = 0
        self._num_examples = 0

    @abstractmethod
    def update(self, predicted, target):
        """Updates the metric's state using the passed batch output.

        By default, this is called once for each batch.
        Args:
            predicted: the output from the model's forward function.
            target: actual values
        """
        self.total_updates += 1
        pass

    def compute(self, save=False):
        if self._num_examples == 0: self.no_sample_error()
        value = self._sum / self._num_examples
        # value = value.data.item()
        if save: self.stored_values.append(value)
        return value

    def no_sample_error(self):
        raise ValueError(self.name, " must have at least one example before it can be computed.")

    def __str__(self):
        return "{}: {:8.3f}".format(self.name, self.compute())


class MAE(Metric):
    """Calculates the mean absolute error."""
    def __init__(self):
        super(MAE, self).__init__()

    def update(self, predicted, target):
        self.total_updates += 1
        num = target.shape[0]
        # absolute_errors = torch.abs(predicted - target.view_as(predicted))
        absolute_errors = torch.abs(predicted - target)
        self._sum += torch.mean(absolute_errors).item() * num
        self._num_examples += target.shape[0]


class MSE(Metric):
    """Calculates the mean squared error."""
    def __init__(self):
        super(MSE, self).__init__()

    def update(self, predicted, target):
        self.total_updates += 1
        num = target.shape[0]
        # squared_errors = torch.pow(predicted - target.view_as(predicted), 2)
        squared_errors = torch.pow(predicted - target, 2)
        self._sum += torch.mean(squared_errors).item() * num
        self._num_examples += num


class Loss(Metric):
    """Calculates the average loss according to the passed loss_fn.

    Args:
        loss_fn (callable): a callable taking a prediction tensor, a target
            tensor, optionally other arguments, and returns the average loss
            over all observations in the batch.
    """
    def __init__(self, loss_fn):
        super(Loss, self).__init__(name=loss_fn.__class__.__name__)
        self._loss_fn = loss_fn

    def update(self, predicted, target, **kwargs):
        self.total_updates += 1
        num = target.shape[0]
        average_loss = self._loss_fn(predicted, target, **kwargs)
        if len(average_loss.shape) != 0:
            raise ValueError("loss_fn did not return the average loss.")
        self._sum += average_loss.item() * num
        self._num_examples += num


class Value(Metric):
    """Keeps track of a value as a metric."""
    def __init__(self, name):
        super(Value, self).__init__(name=name)

    def update(self, avg_value, num):
        self.total_updates += 1
        self._sum += avg_value.data.item() * num
        self._num_examples += num
