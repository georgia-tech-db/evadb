"""
This file gives interface to all query optimizer modules
If any issues arise please contact jaeho.bang@gmail.com

@Jaeho Bang
"""

from abc import ABCMeta, abstractmethod

"""
Initial Design Thoughts:
Query Optimizer by definition should perform two tasks:
1. analyze Structered Query Language
2. Determine efficient execution mechanisms (plans)

"""


class QOTemplate(metaclass=ABCMeta):

    @abstractmethod
    def executeQueries(self, queries: list) -> list:
        """
        Query Optimizer by definition should perform two tasks:
        1. Analyze given Structured Query Language (SQL)
        2. Determine efficient execution mechanisms/plans
        :param queries: input queries / query
        :return: output plans / plan that can be understood by the system
        """
        pass
