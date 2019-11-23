from abc import ABC, abstractmethod
from typing import List


class AbstractPP(ABC):
    """
    An abstract class for PPs
    """

    @abstractmethod
    def predict(self, batch) -> List[bool]:
        pass
