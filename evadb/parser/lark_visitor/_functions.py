# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from lark import Token, Tree

from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.aggregation_expression import AggregationExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_function_statement import CreateFunctionStatement


##################################################################
# Functions - Functions, Aggregate Windowed functions
##################################################################
class Functions:
    def function(self, tree):
        function_name = None
        function_output = None
        function_args = []

        for child in tree.children:
            if isinstance(child, Token):
                if child.value == "*":
                    function_args = [TupleValueExpression(name="*")]
            if isinstance(child, Tree):
                if child.data == "simple_id":
                    function_name = self.visit(child)
                elif child.data == "dotted_id":
                    function_output = self.visit(child)
                elif child.data == "function_args":
                    function_args = self.visit(child)

        func_expr = FunctionExpression(None, name=function_name, output=function_output)
        for arg in function_args:
            func_expr.append_child(arg)

        return func_expr

    def function_args(self, tree):
        args = []
        for child in tree.children:
            if isinstance(child, Tree):
                args.append(self.visit(child))
        return args

    # Create function
    def create_function(self, tree):
        function_name = None
        or_replace = False
        if_not_exists = False
        input_definitions = []
        output_definitions = []
        impl_path = None
        function_type = None
        query = None
        metadata = []

        create_definitions_index = 0
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "function_name":
                    function_name = self.visit(child)
                elif child.data == "or_replace":
                    or_replace = True
                elif child.data == "if_not_exists":
                    if_not_exists = True
                elif child.data == "create_definitions":
                    # There should be 2 createDefinition
                    # idx 0 describing function INPUT
                    # idx 1 describing function OUTPUT
                    if create_definitions_index == 0:
                        input_definitions = self.visit(child)
                        create_definitions_index += 1
                    elif create_definitions_index == 1:
                        output_definitions = self.visit(child)
                elif child.data == "function_type":
                    function_type = self.visit(child)
                elif child.data == "function_impl":
                    impl_path = self.visit(child).value
                elif child.data == "simple_select":
                    query = self.visit(child)
                elif child.data == "function_metadata":
                    # Each function metadata is a key value pair
                    key_value_pair = self.visit(child)
                    # value can be an integer or string
                    value = key_value_pair[1]
                    if isinstance(value, ConstantValueExpression):
                        value = value.value
                    # Removing .value from key_value_pair[0] since key is now an ID_LITERAL
                    # Adding lower() to ensure the key is in lowercase
                    metadata.append((key_value_pair[0].lower(), value)),

        return CreateFunctionStatement(
            function_name,
            or_replace,
            if_not_exists,
            impl_path,
            input_definitions,
            output_definitions,
            function_type,
            query,
            metadata,
        )

    def get_aggregate_function_type(self, agg_func_name):
        agg_func_type = None
        if agg_func_name == "COUNT":
            agg_func_type = ExpressionType.AGGREGATION_COUNT
        elif agg_func_name == "MIN":
            agg_func_type = ExpressionType.AGGREGATION_MIN
        elif agg_func_name == "MAX":
            agg_func_type = ExpressionType.AGGREGATION_MAX
        elif agg_func_name == "SUM":
            agg_func_type = ExpressionType.AGGREGATION_SUM
        elif agg_func_name == "AVG":
            agg_func_type = ExpressionType.AGGREGATION_AVG
        elif agg_func_name == "FIRST":
            agg_func_type = ExpressionType.AGGREGATION_FIRST
        elif agg_func_name == "LAST":
            agg_func_type = ExpressionType.AGGREGATION_LAST
        elif agg_func_name == "SEGMENT":
            agg_func_type = ExpressionType.AGGREGATION_SEGMENT
        return agg_func_type

    def aggregate_windowed_function(self, tree):
        agg_func_arg = None
        agg_func_name = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "function_arg":
                    agg_func_arg = self.visit(child)
                elif child.data == "aggregate_function_name":
                    agg_func_name = self.visit(child).value
            elif isinstance(child, Token):
                token = child.value
                # Support for COUNT(*)
                if token != "*":
                    agg_func_name = token
                else:
                    agg_func_arg = TupleValueExpression(name="id")

        agg_func_type = self.get_aggregate_function_type(agg_func_name)
        agg_expr = AggregationExpression(agg_func_type, None, agg_func_arg)
        return agg_expr
