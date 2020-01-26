from src.query_parser.eva_statement import EvaStatement
from src.query_parser.select_statement import SelectStatement
from src.query_planner.abstract_scan_plan import AbstractScan


class StatementToPlanConvertor():
    def __init__(self):
        self._plan = None

    def visit(self, statement: EvaStatement):
        """Based on the instance of the statement the corresponding visit is called. The logic is hidden from client.
        
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
        
        #Create a logical get node
        video = statement.from_table
        if video is not None:
            visit_table_ref(video)
        
        #Filter Operator
        predicate = statement.where_clause
        if predicate is not None:
            #ToDo Binding the expression 
            filter_opr = LogicalFilter(predicate)
            filter_opr.append_child(self._plan)
            self._plan = filter_opr
        
        #Projection operator
        select_columns = statement.target_list
        #ToDO
        # add support for SELECT STAR
        if select_columns is not None:
            #ToDo Bind the columns using catalog 
            projection_opr = LogicalProject(select_columns)
            projection_opr.append_child(self._plan)
            self._plan = projection_opr

        
    def visit_table_ref(self, video: TableRef):
        """Bind table ref object and convert to Logical get operator
        
        Arguments:
            video {TableRef} -- [Input table ref object created by the parser]
        """
        video_data = None
        #Call catalog with Table ref details to get hold of the storage DataFrame
        #video_data = catalog.get_table_catalog_entry(video.info)
        
        get_opr = LogicalGet(video_data)
        self._plan = get_opr
    @property
    def plan(self):
        return self._plan

    