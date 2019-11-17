"""Data Structure to keep objects of query optimization in memory"""


class Memo:

    def __init__(self):
        self._pp_dict = {}

    def addPP(self, name: str, model_type: str, execution_cost: float) -> None:
        """

        :param name:
        :param model_type:
        :param execution_cost:
        :return:
        """
        self._pp_dict[(name, model_type)] = execution_cost

    def checkPP(self, name: str, model_type: str) -> bool:
        """

        :param name:
        :param model_type:
        :return:
        """
        if (name, model_type) in self._pp_dict:
            return True
        else:
            return False

    def getPP(self, name: str, model_type: str) -> float:
        """

        :param name:
        :param model_type:
        :return:
        """
        if self.checkPP(name, model_type):
            return self._pp_dict[(name, model_type)]
        else:
            raise Exception('(%s, %s) PP not found in memo' % (name, model_type))