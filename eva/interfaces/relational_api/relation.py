from typing import List, Union
from eva.expression.expression_utils import conjunction_list_to_expression_tree
from eva.interfaces.relational_api.utils import (
    execute_statement,
    string_list_to_expression_list,
)
from eva.parser.select_statement import SelectStatement

from eva.parser.statement import AbstractStatement


class EVARelation:
    def __init__(self, stmt: AbstractStatement):
        self._eva_statement: AbstractStatement = stmt

    def select(self, exprs: Union[str, List[str]]):
        assert isinstance(self._eva_statement, SelectStatement)

        exprs = [exprs] if isinstance(exprs, str) else exprs
        parsed_exprs = string_list_to_expression_list(exprs)

        self._eva_statement.target_list = parsed_exprs

        return self

    def filter(self, expr: str):
        assert isinstance(self._eva_statement, SelectStatement)
        parsed_expr = string_list_to_expression_list([expr])[0]

        if self._eva_statement.where_clause is None:
            self._eva_statement.where_clause = parsed_expr
        else:
            # AND the clause with the existing expression
            self._eva_statement.where_clause = conjunction_list_to_expression_tree(
                self._eva_statement.where_clause, parsed_expr
            )

        return self

    def execute(self):
        result = execute_statement(self._eva_statement)
        assert result.frames is not None
        return result.frames

    def show(self):
        return self.execute()
