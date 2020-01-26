from src.query_parser.eva_statement import EvaStatement
from src.query_parser.select_statement import SelectStatement
from src.query_planner.abstract_scan_plan import AbstractScan


class StatementToPlanConvertor():
    def __init__(self):
        self._plan = None

    def visit(self, statement: EvaStatement):
        """Based on the instance of the statement the corresponding visit is called. The logic is heidden form client.
        
        Arguments:
            statement {EvaStatement} -- [Input statement]
        """
        if isinstance(statement, SelectStatement):
            visit_select(statement)

    def visit_select(self, statement: EvaStatement):
        """convertor for select statement
        
        Arguments:
            statement {EvaStatement} -- [input select statement]
        """
        video = statement.from_table
        #data table binding goes here
        #use the catalog
        select_columns = statement.target_list
        #binding for columns has to be done here
        predicate = statement.where_clause

        logical_plan = AbstractScan(select_columns, video, predicate)
        self._plan = logical_plan

    @property
    def plan(self):
        return self._plan

    