# IMPORT MODULES
from src.query_parser.eva_statement import EvaStatement
from src.query_parser.types import StatementType
from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractLoader
from src.query_parser.table_ref import TableRef
from typing import List

# INIT CLASS FOR INSERT STATEMENT
class InsertStatement(EvaStatement):
    """
    Insert Statement constructed after parsing the input query
    Attributes
    ----------
    _target_list : List[AbstractExpression]
        list of target attributes in the insert query,
        each attribute is represented as a Abstract Expression
    _to_table : TableRef
        table reference in the insert query
    **kwargs : to support other functionality, Orderby, Distinct, Groupby.
    """

    def __init__(self, target_list: List[AbstractExpression] = None,
                 to_table: TableRef = None,
                 **kwargs):
        super().__init__(StatementType.INSERT)
        self._to_table = to_table
        self._target_list = target_list

    # DATA TO BE INSERTED
    @property
    def target_list(self):
        return self._target_list
    
    # SET TARGET LIST
    @target_list.setter
    def target_list(self, target_expr_list: List[AbstractExpression]):
        self._target_list = target_expr_list
        
    # INSERT INTO THE FOLLOWING TABLE
    @property
    def to_table(self):
        return self._to_table

    # SET TABLE
    @to_table.setter
    def to_table(self, table: TableRef):
        self._to_table = table

    # SQL FOR INSERTING INTO EVA - PARSER    
    def __str__(self) -> str:
        print_str = "INSERT INTO {} VALUES {}".format(self._to_table,
                                                        self._target_list)
        return print_str
