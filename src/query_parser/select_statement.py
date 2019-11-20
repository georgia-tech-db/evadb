from src.query_parser.eva_statement import EvaStatement
from src.query_parser.eva_statement import StatementType
from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractLoader
from typing import List

class SelectStatement(EvaStatement):
    """Select Statemet 
    
    Attributes
    ----------
    _select_elements : List[AbstractExpression]
        select elements in the select statement
    _from_table : AbstractLoader
        from part of the select query
    _where_clause : AbstractExpression
        predicate of the select statement
    """

    def __init__(self, select_elements = None, from_table = None, where_clause=None):
        super().__init__(StatementType.SELECT)
        self._from_table = from_table
        self._where_clause = where_clause
        self._select_elements = select_elements
    
    @property
    def where_clause(self):
        return self._where_clause
    
    @where_clause.setter
    def where_clause(self, where_expr : AbstractExpression):
        self._where_clause = where_expr

    @property
    def select_elements(self):
        return self._select_elements
    
    @select_elements.setter
    def select_elements(self, select_expr_list : List[AbstractExpression]):
        self._select_elements = select_expr_list

    @property
    def from_table(self):
        return self._from_table

    @from_table.setter
    def from_table(self, table : AbstractLoader):
        self._from_table = table
    
    