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
from eva.catalog.column_type import ColumnType, Dimension, NdArrayType
from eva.parser.create_mat_view_statement import CreateMaterializedViewStatement
from eva.parser.create_statement import (
    ColConstraintInfo,
    ColumnDefinition,
    CreateTableStatement,
)
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.table_ref import TableRef
from eva.parser.types import ColumnConstraintEnum
from eva.utils.logging_manager import logger


##################################################################
# CREATE STATEMENTS
##################################################################
class CreateTable(evaql_parserVisitor):
    def visitColumnCreateTable(self, ctx: evaql_parser.ColumnCreateTableContext):

        table_ref = None
        if_not_exists = False
        create_definitions = []

        # first two children will be CREATE TABLE terminal token
        for child in ctx.children[2:]:
            try:
                rule_idx = child.getRuleIndex()

                if rule_idx == evaql_parser.RULE_tableName:
                    table_ref = TableRef(self.visit(ctx.tableName()))

                elif rule_idx == evaql_parser.RULE_ifNotExists:
                    if_not_exists = True

                elif rule_idx == evaql_parser.RULE_createDefinitions:
                    create_definitions = self.visit(ctx.createDefinitions())

            except BaseException:
                # stop parsing something bad happened
                return None

        create_stmt = CreateTableStatement(table_ref, if_not_exists, create_definitions)
        return create_stmt

    def visitCreateDefinitions(self, ctx: evaql_parser.CreateDefinitionsContext):
        column_definitions = []
        child_index = 0
        for child in ctx.children:
            create_definition = ctx.createDefinition(child_index)
            if create_definition is not None:
                column_definition = self.visit(create_definition)
                column_definitions.append(column_definition)
            child_index = child_index + 1

        return column_definitions

    def visitColumnDeclaration(self, ctx: evaql_parser.ColumnDeclarationContext):

        data_type, array_type, dimensions, column_constraint_information = self.visit(
            ctx.columnDefinition()
        )

        column_name = self.visit(ctx.uid())

        if column_name is not None:
            return ColumnDefinition(
                column_name,
                data_type,
                array_type,
                dimensions,
                column_constraint_information,
            )

    def visitColumnDefinition(self, ctx: evaql_parser.ColumnDefinitionContext):

        data_type, array_type, dimensions = self.visit(ctx.dataType())

        constraint_count = len(ctx.columnConstraint())

        column_constraint_information = ColConstraintInfo()

        not_null_set = False
        for i in range(constraint_count):
            return_type = self.visit(ctx.columnConstraint(i))
            if return_type == ColumnConstraintEnum.UNIQUE:
                column_constraint_information.unique = True
                column_constraint_information.nullable = False
                not_null_set = True
            elif return_type == ColumnConstraintEnum.NOTNULL:
                column_constraint_information.nullable = False
                not_null_set = True

        if not not_null_set:
            column_constraint_information.nullable = True

        return data_type, array_type, dimensions, column_constraint_information

    def visitUniqueKeyColumnConstraint(
        self, ctx: evaql_parser.UniqueKeyColumnConstraintContext
    ):
        return ColumnConstraintEnum.UNIQUE

    def visitNullColumnConstraint(self, ctx: evaql_parser.NullColumnConstraintContext):
        return ColumnConstraintEnum.NOTNULL

    def visitSimpleDataType(self, ctx: evaql_parser.SimpleDataTypeContext):

        data_type = None
        array_type = None
        dimensions = []

        if ctx.BOOLEAN() is not None:
            data_type = ColumnType.BOOLEAN

        return data_type, array_type, dimensions

    def visitIntegerDataType(self, ctx: evaql_parser.IntegerDataTypeContext):

        data_type = None
        array_type = None
        dimensions = []

        if ctx.INTEGER() is not None:
            data_type = ColumnType.INTEGER
        elif ctx.UNSIGNED() is not None:
            data_type = ColumnType.INTEGER

        return data_type, array_type, dimensions

    def visitDimensionDataType(self, ctx: evaql_parser.DimensionDataTypeContext):
        data_type = None
        array_type = None
        dimensions = []

        if ctx.FLOAT() is not None:
            data_type = ColumnType.FLOAT
            dimensions = self.visit(ctx.lengthTwoDimension())
        elif ctx.TEXT() is not None:
            data_type = ColumnType.TEXT
            dimensions = self.visit(ctx.lengthOneDimension())

        return data_type, array_type, dimensions

    def visitArrayDataType(self, ctx: evaql_parser.ArrayDataTypeContext):
        data_type = ColumnType.NDARRAY
        array_type = None
        dimensions = None
        if ctx.arrayType():
            array_type = self.visit(ctx.arrayType())
        else:
            array_type = NdArrayType.ANYTYPE
        if ctx.lengthDimensionList():
            dimensions = self.visit(ctx.lengthDimensionList())
        return data_type, array_type, dimensions

    def visitAnyDataType(self, ctx: evaql_parser.AnyDataTypeContext):
        return ColumnType.ANY, None, []

    def visitArrayType(self, ctx: evaql_parser.ArrayTypeContext):
        array_type = None

        if ctx.INT8() is not None:
            array_type = NdArrayType.INT8
        elif ctx.UINT8() is not None:
            array_type = NdArrayType.UINT8
        elif ctx.INT16() is not None:
            array_type = NdArrayType.INT16
        elif ctx.INT32() is not None:
            array_type = NdArrayType.INT32
        elif ctx.INT64() is not None:
            array_type = NdArrayType.INT64
        elif ctx.UNICODE() is not None:
            array_type = NdArrayType.UNICODE
        elif ctx.BOOL() is not None:
            array_type = NdArrayType.BOOL
        elif ctx.FLOAT32() is not None:
            array_type = NdArrayType.FLOAT32
        elif ctx.FLOAT64() is not None:
            array_type = NdArrayType.FLOAT64
        elif ctx.DECIMAL() is not None:
            array_type = NdArrayType.DECIMAL
        elif ctx.STR() is not None:
            array_type = NdArrayType.STR
        elif ctx.DATETIME() is not None:
            array_type = NdArrayType.DATETIME
        elif ctx.ANYTYPE() is not None:
            array_type = NdArrayType.ANYTYPE
        else:
            err_msg = "Unsupported NdArray datatype found in the query"
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        return array_type

    def visitLengthOneDimension(self, ctx: evaql_parser.LengthOneDimensionContext):
        dimensions = []

        if ctx.decimalLiteral() is not None:
            dimensions = [self.visit(ctx.decimalLiteral())]

        return dimensions

    def visitLengthTwoDimension(self, ctx: evaql_parser.LengthTwoDimensionContext):
        first_decimal = self.visit(ctx.decimalLiteral(0))
        second_decimal = self.visit(ctx.decimalLiteral(1))

        dimensions = [first_decimal, second_decimal]
        return dimensions

    def visitLengthDimensionList(self, ctx: evaql_parser.LengthDimensionListContext):
        dimensions = []
        dimension_list_length = len(ctx.decimalLiteral())
        for dimension_list_index in range(dimension_list_length):
            decimal_literal = ctx.decimalLiteral(dimension_list_index)
            decimal = self.visit(decimal_literal)
            dimensions.append(decimal)

        return dimensions

    def visitDecimalLiteral(self, ctx: evaql_parser.DecimalLiteralContext):

        decimal = None
        if ctx.DECIMAL_LITERAL() is not None:
            decimal = int(str(ctx.DECIMAL_LITERAL()))
        elif ctx.ONE_DECIMAL() is not None:
            decimal = int(str(ctx.ONE_DECIMAL()))
        elif ctx.TWO_DECIMAL() is not None:
            decimal = int(str(ctx.TWO_DECIMAL()))
        elif ctx.ZERO_DECIMAL() is not None:
            decimal = int(str(ctx.ZERO_DECIMAL()))
        elif ctx.ANYDIM() is not None:
            decimal = Dimension.ANYDIM
        return decimal

    # MATERIALIZED VIEW
    def visitCreateMaterializedView(
        self, ctx: evaql_parser.CreateMaterializedViewContext
    ):
        view_name = self.visit(ctx.tableName())
        view_ref = TableRef(view_name)
        if_not_exists = False
        if ctx.ifNotExists():
            if_not_exists = True
        uid_list = self.visit(ctx.uidList())
        # setting all other column definition attributes as None,
        # need to figure from query
        col_list = [
            ColumnDefinition(uid.col_name, None, None, None) for uid in uid_list
        ]
        query = self.visit(ctx.selectStatement())
        return CreateMaterializedViewStatement(view_ref, col_list, if_not_exists, query)
