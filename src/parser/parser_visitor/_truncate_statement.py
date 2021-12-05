from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.table_ref import TableRef, TableInfo
from src.parser.truncate_statement import TruncateTableStatement
from src.parser.evaql.evaql_parser import evaql_parser
import warnings

# Modified
##################################################################
# TRUNCATE STATEMENTS
##################################################################
class TruncateTable(evaql_parserVisitor):
    def visitTruncateTable(self, ctx: evaql_parser.TruncateTableContext):
        table_ref = TableRef(self.visit(ctx.tableName()))
        truncate_stmt = TruncateTableStatement(table_ref)
        return truncate_stmt