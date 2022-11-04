# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from antlr4 import TerminalNode

from eva.expression.abstract_expression import ExpressionType
from eva.expression.aggregation_expression import AggregationExpression
from eva.expression.function_expression import FunctionExpression
from eva.parser.create_udf_statement import CreateUDFStatement
from eva.parser.drop_udf_statement import DropUDFStatement
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.utils.logging_manager import logger


##################################################################
# Functions - UDFs, Aggregate Windowed functions
##################################################################
class Functions(evaql_parserVisitor):
    def visitUdfFunction(self, ctx: evaql_parser.UdfFunctionContext):
        udf_name = None
        udf_output = None
        if ctx.simpleId():
            udf_name = self.visit(ctx.simpleId())
        else:
            logger.error("UDF function name missing.")
        if ctx.dottedId():
            udf_output = self.visit(ctx.dottedId())

        udf_args = self.visit(ctx.functionArgs())
        func_expr = FunctionExpression(None, name=udf_name, output=udf_output)
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

    # Get UDF information from context
    def getUDFInfo(self, ctx):
        udf_name = None
        if_not_exists = False
        if_exists = False
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

                elif rule_idx == evaql_parser.RULE_ifExists:
                    if_exists = True

                elif rule_idx == evaql_parser.RULE_createDefinitions:
                    # There should be 2 createDefinition
                    # idx 0 describing udf INPUT
                    # idx 1 describing udf OUTPUT
                    if len(ctx.createDefinitions()) != 2:
                        err_msg = "Mising UDF Input or Output"
                        logger.error(err_msg)
                        raise SyntaxError(err_msg)
                    input_definitions = self.visit(ctx.createDefinitions(0))
                    output_definitions = self.visit(ctx.createDefinitions(1))

                elif rule_idx == evaql_parser.RULE_udfType:
                    udf_type = self.visit(ctx.udfType())

                elif rule_idx == evaql_parser.RULE_udfImpl:
                    impl_path = self.visit(ctx.udfImpl()).value

            except BaseException:
                logger.error("CREATE/DROP UDF Failed")
                # stop parsing something bad happened
                return None

        if if_exists and if_not_exists:
            logger.error("Bad CREATE/DROP UDF command syntax")

        return (
            udf_name,
            if_exists or if_not_exists,
            input_definitions,
            output_definitions,
            impl_path,
            udf_type,
        )

    # Drop UDF
    def visitDropUdf(self, ctx: evaql_parser.DropUdfContext):
        udf_info = self.getUDFInfo(ctx)
        stmt = DropUDFStatement(*udf_info[:2])
        return stmt

    # Create UDF
    def visitCreateUdf(self, ctx: evaql_parser.CreateUdfContext):
        udf_info = self.getUDFInfo(ctx)
        stmt = CreateUDFStatement(*udf_info)
        return stmt

    def visitAggregateWindowedFunction(
        self, ctx: evaql_parser.AggregateWindowedFunctionContext
    ):
        if ctx.aggregateFunctionName():
            agg_func_name = self.visit(ctx.aggregateFunctionName())
        else:
            logger.error("Aggregate function name missing.")
        agg_func_type = self.getAggregateFunctionType(agg_func_name)
        agg_func_arg = self.visit(ctx.functionArg())
        agg_expr = AggregationExpression(agg_func_type, None, agg_func_arg)

        return agg_expr

    def visitAggregateFunctionName(
        self, ctx: evaql_parser.AggregateFunctionNameContext
    ):
        return ctx.getText()

    def getAggregateFunctionType(self, agg_func_name):
        agg_func_type = None
        if agg_func_name == "FIRST":
            agg_func_type = ExpressionType.AGGREGATION_FIRST
        elif agg_func_name == "LAST":
            agg_func_type = ExpressionType.AGGREGATION_LAST
        elif agg_func_name == "SEGMENT":
            agg_func_type = ExpressionType.AGGREGATION_SEGMENT
        else:
            logger.error("Aggregate Function {} not supported.".format(agg_func_name))
        return agg_func_type
