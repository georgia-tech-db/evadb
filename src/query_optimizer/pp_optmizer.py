"""Finds Optimal Probabilistic Predicates for an expression"""
from src.expression.abstract_expression import AbstractExpression
from src.catalog.catalog import Catalog
import constants


class PPOptmizer:

    def __init__(self, catalog: Catalog, predicates: list, accuracy_budget: float = 0.9):
        self._catalog = catalog
        self._pp_handler = self._catalog.getProbPredicateHandler()
        self._predicates = predicates
        self.accuracy_budget = accuracy_budget

    def _get_pp_stats(self) -> dict:
        """Query PP Stats from Catalog

        :return:
        dict, A dictionary containing cost information of all pp filters
        """
        filter_names = self._pp_handler.listProbilisticFilters()
        filter_names = [f[0] for f in filter_names]
        stats = {}
        for f in filter_names:
            rows = self._pp_handler.getProbabilisticFilter(f)
            filter_dict = {}
            for row in rows:
                filter_dict[row[7]] = {'R': row[2], 'C': row[3], 'A': row[4]}
            stats[f] = filter_dict
        return stats

    def _wrangler(self, expression: AbstractExpression, label_desc: dict) -> list:
        """ Generate possible enumerations of the `expression`

        :param expression: An Abstract Expression (usually Logical Expression)
        :param label_desc: Description of all possible PP filters of a type
        :return:
        list, A list of Logical Expressions which are possible enumerations of the input expression
        """

        pass

    def _compute_expression_costs(self, expression: AbstractExpression) -> float:
        """Compute cost of applying PP filters to an expression

        :param expression: Input Expression (Logical Expression)
        :return: Execution Cost of the  expressions
        """
        pass

    def _compute_cost_red_rate(self, cost: float, reduction_rate: float) -> float:
        """Compute Execution Cost of PP filter"""
        assert (0 <= reduction_rate <= 1)
        if reduction_rate == 0:
            reduction_rate = 0.000001
        return cost / reduction_rate

    def execute(self):
        """Finds optimal order expression based on PP execution cost evaluation."""

        stats = self._get_pp_stats()
        filter_names = stats.keys()

        # TODO: Need to query this from DB. Check how to do this. Or we cal split the filter names to generate this.
        label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
                      "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
                      "c": [constants.DISCRETE,
                            ["white", "red", "black", "silver"]],
                      "i": [constants.DISCRETE,
                            ["pt335", "pt342", "pt211", "pt208"]],
                      "o": [constants.DISCRETE,
                            ["pt335", "pt342", "pt211", "pt208"]]}

        # TODO: Generalize this all list of expression. A for loop.
        expr = self._predicates[0]
        enumerations = self._wrangler(expr, label_desc)



if __name__ == '__main__':

    catalog = Catalog(constants.UADETRAC)
    pp_handler = catalog.getProbPredicateHandler()
    pp_filter_names = pp_handler.listProbilisticFilters()
    pp_filter_names = [f[0] for f in pp_filter_names]
    # stats = {}
    # for f in pp_filter_names:
    #     filter_rows = pp_handler.getProbabilisticFilter(f)
    #     filter_dict = {}
    #     for row in filter_rows:
    #         filter_dict[row[7]]= {'R': row[2], 'C': row[3], 'A': row[4]}
    #     stats[f] = filter_dict
    # print(stats)
    print(pp_filter_names)