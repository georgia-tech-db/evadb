from src.query_parser.eva_statement import EvaStatement
from src.query_parser.types import StatementType
from src.expression.abstract_expression import AbstractExpression
from src.query_parser.table_ref import TableRef
from typing import List


class SelectStatement(EvaStatement):
    """
    Select Statement constructed after parsing the input query

    Attributes
    ----------
    _target_list : List[AbstractExpression]
        list of target attributes in the select query,
        each attribute is represented as a Abstract Expression
    _from_table : TableRef
        table reference in the select query
    _where_clause : AbstractExpression
        predicate of the select query, represented as a expression tree.
    **kwargs : to support other functionality, Orderby, Distinct, Groupby.
    """

    def __init__(self, target_list: List[AbstractExpression] = None,
                 from_table: TableRef = None,
                 where_clause: AbstractExpression = None,
                 **kwargs):
        super().__init__(StatementType.SELECT)
        self._from_table = from_table
        self._where_clause = where_clause
        self._target_list = target_list

    @property
    def where_clause(self):
        return self._where_clause

    @where_clause.setter
    def where_clause(self, where_expr: AbstractExpression):
        self._where_clause = where_expr

    @property
    def target_list(self):
        return self._target_list

    @target_list.setter
    def target_list(self, target_expr_list: List[AbstractExpression]):
        self._target_list = target_expr_list

    @property
    def from_table(self):
        return self._from_table

    @from_table.setter
    def from_table(self, table: TableRef):
        self._from_table = table

    def __str__(self) -> str:
        print_str = "SELECT {} FROM {} WHERE {}".format(self._target_list,
                                                        self._from_table,
                                                        self._where_clause)
        return print_str
