from abc import ABC, abstractmethod
from typing import List


class BasePrediction(ABC):
    """Base class for any type of prediction from model"""

    @abstractmethod
    def eq(self, element) -> bool:
        """
        Checks if prediction is equal to the element
        Arguments:
            element (object): Check if element is equivalent
        Returns:
            bool (True if equal else False)
        """
        pass

    @abstractmethod
    def contains(self, element) -> bool:
        """
        Checks if the prediction contains the element
        Arguments:
            element (object): Element to be checked
        Returns:
            bool (True if contains else False)
        """
        pass

    @abstractmethod
    def has_one(self, elements: List[object]) -> bool:
        """
        This method is used for defining the 'IN' operation
        Arguments:
            elements (List[object]): if the predictions are in the given list
        Returns:
            bool
        """
        pass
