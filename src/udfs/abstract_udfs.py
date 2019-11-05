from abc import ABCMeta, abstractmethod
from typing import List

from src.models import FrameBatch, FrameInfo, Prediction


class AbstractClassifierUDF(metaclass=ABCMeta):
    """
    Abstract class for UDFs. All the UDFs which perform classification inherit this calls.

    Load and initialize the machine learning model in the __init__.

    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def input_format(self) -> FrameInfo:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def labels(self) -> List[str]:
        """
        Returns:
            List[str]: list of labels the classifier predicts
        """
        pass

    @abstractmethod
    def classify(self, batch: FrameBatch) -> List[Prediction]:
        """
        Takes as input a batch of frames and returns the predictions by applying the classification model.

        Arguments:
            batch (FrameBatch): Input batch of frames on which prediction needs to be made

        Returns:
            List[Prediction]: The predictions made by the classifier
        """
        pass
