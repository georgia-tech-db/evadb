

from src.parser.evaql.evaql_parser import evaql_parser



##################################################################
# SELECT STATEMENT
##################################################################

def visitSimpleSelect(self, ctx: evaql_parser.SimpleSelectContext):
    select_stmt = self.visitChildren(ctx)
    return select_stmt