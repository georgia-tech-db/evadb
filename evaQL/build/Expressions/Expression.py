from abc import ABCMeta, abstractmethod

class Expression(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def evaluate(self):
        pass

