"""Finds Optimal Probabilistic Predicates for an expression"""
import src.constants as constants
from src.catalog.catalog import Catalog
from src.expression.abstract_expression import AbstractExpression, ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import LogicalExpression
from src.query_optimizer.memo import Memo


class PPOptmizer:

    def __init__(self, catalog: Catalog, predicates: list, accuracy_budget: float = 0.9):
        self._catalog = catalog
        self._memo = Memo()
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

    def _find_model(self, pp_name, pp_stats, accuracy_budget=0.9):
        possible_models = pp_stats[pp_name]
        best = []

        for possible_model in possible_models:
            if possible_models[possible_model]["A"] < accuracy_budget:
                continue
            if best == []:
                best = [possible_model, self._compute_cost_red_rate(
                    possible_models[possible_model]["C"],
                    possible_models[possible_model]["R"]),
                        possible_models[possible_model]["R"]]
            else:
                alternative_best_cost = self._compute_cost_red_rate(
                    possible_models[possible_model]["C"],
                    possible_models[possible_model]["R"])
                if alternative_best_cost < best[1]:
                    best = [possible_model, alternative_best_cost,
                            possible_models[possible_model]["R"]]

        if best == []:
            return None, 0
        else:
            return best[0], best[2]

    def _wrangler(self, expression: LogicalExpression, label_desc: dict) -> list:
        """ Generate possible enumerations of the `expression`

        TODO: Currently supporting LogicalExpression, but its a easy modification to support AbstractExpression

        :param expression: A Logical Expression
        :param label_desc: Description of all possible PP filters of a type
        :return:
        list, A list of Logical Expressions which are possible enumerations of the input expression
        """
        leftExpr = expression.getLeftExpression()
        rightExpr = expression.getRightExpression()
        operator = expression.getOperator()  # AND / OR

        new_left_exprs = [leftExpr]
        new_right_exprs = [rightExpr]

        # Explore left expr
        if leftExpr is not None:
            if leftExpr.etype == ExpressionType.COMPARE_EQUAL or leftExpr.etype == ExpressionType.COMPARE_NOT_EQUAL:
                lValue = leftExpr.getLeft().evaluate()
                rValue = leftExpr.getRight().evaluate()
                rValues = label_desc[lValue][1]  # fetching all possible rvalues
                new_not_expr = None
                for rVal in rValues:
                    if rVal != rValue:
                        new_r_expr = ConstantValueExpression(rVal)

                        # TODO extract out this in a function
                        if leftExpr.etype == ExpressionType.COMPARE_EQUAL:
                            new_exptype = ExpressionType.COMPARE_NOT_EQUAL
                        else:
                            new_exptype = ExpressionType.COMPARE_EQUAL

                        new_comp_expr = ComparisonExpression(new_exptype, leftExpr.getLeft(), new_r_expr)
                        if not new_not_expr:
                            new_not_expr = new_comp_expr
                        else:
                            new_not_expr = LogicalExpression(new_not_expr, 'AND', new_comp_expr)
                new_left_exprs.append(new_not_expr)
            elif leftExpr.etype == ExpressionType.COMPARE_LOGICAL:
                new_left_exprs.extend(self._wrangler(leftExpr, label_desc))

        # Explore right expr
        if rightExpr is not None:
            if rightExpr.etype == ExpressionType.COMPARE_EQUAL or rightExpr.etype == ExpressionType.COMPARE_NOT_EQUAL:
                lValue = rightExpr.getLeft().evaluate()
                rValue = rightExpr.getRight().evaluate()
                rValues = label_desc[lValue][1]  # fetching all possible rvalues
                new_not_expr = None
                for rVal in rValues:
                    if rVal != rValue:
                        new_r_expr = ConstantValueExpression(rVal)

                        if rightExpr.etype == ExpressionType.COMPARE_EQUAL:
                            new_exptype = ExpressionType.COMPARE_NOT_EQUAL
                        else:
                            new_exptype = ExpressionType.COMPARE_EQUAL

                        new_comp_expr = ComparisonExpression(new_exptype, rightExpr.getLeft(), new_r_expr)
                        if not new_not_expr:
                            new_not_expr = new_comp_expr
                        else:
                            new_not_expr = LogicalExpression(new_not_expr, 'AND', new_comp_expr)
                new_right_exprs.append(new_not_expr)
            elif rightExpr.etype == ExpressionType.COMPARE_LOGICAL:
                new_right_exprs.extend(self._wrangler(leftExpr, label_desc))

        enumerated_exprs = []
        for left in new_left_exprs:
            for right in new_right_exprs:
                new_logical_expr = LogicalExpression(left, operator, right)
                enumerated_exprs.append(new_logical_expr)
        return enumerated_exprs

    def _compute_expression_costs(self, expression: AbstractExpression, stats: dict) -> float:
        """Compute cost of applying PP filters to an expression

        :param expression: Input Expression (Logical Expression)
        :return: Execution Cost of the  expressions
        """
        if isinstance(expression, LogicalExpression):
            left_expression = expression.getLeftExpression()
            right_expression = expression.getRightExpression()
            left_cost, right_cost = 0.999, 0.999

            if isinstance(left_expression, LogicalExpression):
                left_cost = self._compute_expression_costs(left_expression, stats)
            elif isinstance(left_expression, ComparisonExpression):
                left_str_expr = str(left_expression)
                if left_str_expr in stats.keys():
                    _, left_cost = self._find_model(left_str_expr, stats)

            if isinstance(right_expression, LogicalExpression):
                right_cost = self._compute_expression_costs(right_expression, stats)
            elif isinstance(right_expression, ComparisonExpression):
                right_str_expr = str(right_expression)
                if right_str_expr in stats.keys():
                    _, right_cost = self._find_model(right_str_expr, stats)

            if expression.operator == "AND":
                reduction_rate = left_cost + right_cost - left_cost * right_cost
            elif expression.operator == "OR":
                reduction_rate = left_cost * right_cost
            else:
                raise ValueError("Invalid operator: " + expression.operator)

            return reduction_rate

    def _compute_cost_red_rate(self, cost: float, reduction_rate: float) -> float:
        """Compute Execution Cost of PP filter"""
        assert (0 <= reduction_rate <= 1)
        if reduction_rate == 0:
            reduction_rate = 0.000001
        return cost / reduction_rate

    def execute(self):
        """Finds optimal order expression based on PP execution cost evaluation."""

        stats = self._get_pp_stats()

        # TODO: Need to query this from DB. Check how to do this. Or we cal split the filter names to generate this.
        label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
                      "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
                      "c": [constants.DISCRETE,
                            ["white", "red", "black", "silver"]],
                      "i": [constants.DISCRETE,
                            ["pt335", "pt342", "pt211", "pt208"]],
                      "o": [constants.DISCRETE,
                            ["pt335", "pt342", "pt211", "pt208"]]}

        # TODO: Generalize this all list of expression. A loop.
        expr = self._predicates[0]
        enumerations = self._wrangler(expr, label_desc)
        candidate_cost_list = []
        for candidate in enumerations:
            execution_cost = self._compute_expression_costs(candidate, stats)
            candidate_cost_list.append((candidate, execution_cost))

        # Sort based on optimal execution cost
        def sort_on_second_index(x):
            return x[1]

        candidate_cost_list.sort(key=sort_on_second_index)
        # return the best candidate
        return candidate_cost_list[0]


if __name__ == '__main__':
    # catalog = Catalog(constants.UADETRAC)
    # pp_handler = catalog.getProbPredicateHandler()
    # pp_filter_names = pp_handler.listProbilisticFilters()
    # pp_filter_names = [f[0] for f in pp_filter_names]
    # print(pp_filter_names)
    const_exp_01 = ConstantValueExpression("t")
    const_exp_02 = ConstantValueExpression("suv")
    cmpr_exp1 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_01, const_exp_02)

    const_exp_11 = ConstantValueExpression("c")
    const_exp_12 = ConstantValueExpression("white")
    cmpr_exp2 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_11, const_exp_12)

    const_exp_21 = ConstantValueExpression("c")
    const_exp_22 = ConstantValueExpression("white")
    cmpr_exp3 = ComparisonExpression(ExpressionType.COMPARE_NOT_EQUAL, const_exp_21, const_exp_22)

    logical_expr1 = LogicalExpression(cmpr_exp1, 'AND', cmpr_exp2)
    logical_expr2 = LogicalExpression(cmpr_exp1, 'AND', cmpr_exp3)

    catalog = Catalog(constants.UADETRAC)
    predicates = [logical_expr2]
    pp_optimizer = PPOptmizer(catalog, predicates)
    out = pp_optimizer.execute()
