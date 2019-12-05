from abc import ABC, abstractmethod
from typing import List


class BasePrediction(ABC):
    """
    Base class for any type of prediction from model.
    Subclasses should override the comparators which are suitable for them.
    All the comparators default to False.
    """

    def __eq__(self, other):
        """
        Checks if prediction is equal to the element
        Arguments:
            element (object): Check if element is equivalent
        Returns:
            bool (True if equal else False)
        """
        return False

    def __contains__(self, element) -> bool:
        """
        Checks if the prediction contains the element
        Arguments:
            element (object): Element to be checked
        Returns:
            bool (True if contains else False)
        """
        return False

    def __gt__(self, other):
        """
        Checks for > operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return False

    def __ge__(self, other):
        """
        Checks for >= operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return self > other and self == other

    def __lt__(self, other):
        """
        Checks for < operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return False

    def __le__(self, other):
        """
        Checks for <= operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if less than or equal)
        """
        return self < other and self == other

    def __ne__(self, other):
        """
        Checks for not equals operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if not equal)
        """
        return not (self == other)
