
from antlr4 import TerminalNode

from src.expression.function_expression import FunctionExpression

from src.parser.create_udf_statement import CreateUDFStatement

from src.parser.evaql.evaql_parser import evaql_parser

from src.utils.logging_manager import LoggingLevel, LoggingManager


##################################################################
# Functions - UDFs, Aggregate Windowed functions
##################################################################
def visitUdfFunction(self, ctx: evaql_parser.UdfFunctionContext):
    udf_name = None
    udf_args = None
    if ctx.simpleId():
        udf_name = self.visit(ctx.simpleId())
    else:
        LoggingManager().log('UDF function name missing.',
                             LoggingLevel.ERROR)

    udf_args = self.visit(ctx.functionArgs())
    func_expr = FunctionExpression(None, name=udf_name)
    for arg in udf_args:
        func_expr.append_child(arg)
    return func_expr


def visitFunctionArgs(self, ctx: evaql_parser.FunctionArgsContext):
    args = []
    for child in ctx.children:
        # ignore COMMAs
        if not isinstance(child, TerminalNode):
            args.append(self.visit(child))
    return args


# Create UDF
def visitCreateUdf(self, ctx: evaql_parser.CreateUdfContext):
    udf_name = None
    if_not_exists = False
    input_definitions = []
    output_definitions = []
    impl_path = None
    udf_type = None

    for child in ctx.children:
        try:
            if isinstance(child, TerminalNode):
                continue
            rule_idx = child.getRuleIndex()

            if rule_idx == evaql_parser.RULE_udfName:
                udf_name = self.visit(ctx.udfName())

            elif rule_idx == evaql_parser.RULE_ifNotExists:
                if_not_exists = True

            elif rule_idx == evaql_parser.RULE_createDefinitions:
                # There should be 2 createDefinition
                # idx 0 describing udf INPUT
                # idx 1 describing udf OUTPUT
                if len(ctx.createDefinitions()) != 2:
                    LoggingManager().log('UDF Input or Output Missing',
                                         LoggingLevel.ERROR)
                input_definitions = self.visit(ctx.createDefinitions(0))
                output_definitions = self.visit(ctx.createDefinitions(1))

            elif rule_idx == evaql_parser.RULE_udfType:
                udf_type = self.visit(ctx.udfType())

            elif rule_idx == evaql_parser.RULE_udfImpl:
                impl_path = self.visit(ctx.udfImpl()).value

        except BaseException:
            LoggingManager().log('CREATE UDF Failed', LoggingLevel.ERROR)
            # stop parsing something bad happened
            return None
    stmt = CreateUDFStatement(
        udf_name,
        if_not_exists,
        input_definitions,
        output_definitions,
        impl_path,
        udf_type)
    return stmt
