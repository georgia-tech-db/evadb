from abc import ABCMeta, abstractmethod


class Optimizer(metaclass=ABCMeta):
    @abstractmethod
    def run(self, queries: list) -> list:
        pass