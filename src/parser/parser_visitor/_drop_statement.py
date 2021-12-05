from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.table_ref import TableRef, TableInfo
from src.parser.drop_statement import DropTableStatement
from src.parser.evaql.evaql_parser import evaql_parser


class DropTable(evaql_parserVisitor):

    def visitTables(self, ctx: evaql_parser.TablesContext):
        tables = []
        for child in ctx.children:
            tables.append(TableRef(self.visit(child)))
        return tables

    def visitDropTable(self, ctx: evaql_parser.DropTableContext):
        # table_ref = None
        if_exists = False
        for child in ctx.children[2:]:
            if child.getRuleIndex() == evaql_parser.RULE_ifExists:
                if_exists = True
        tables_to_drop = self.visit(ctx.tables())

        drop_stmt = DropTableStatement(tables_to_drop, if_exists=if_exists)
        return drop_stmt
