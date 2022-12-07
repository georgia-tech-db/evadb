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

from eva.expression.function_expression import FunctionExpression
from eva.parser.create_index_statement import CreateIndexStatement
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.table_ref import TableRef
from eva.expression.tuple_value_expression import TupleValueExpression

from eva.catalog.column_type import FaissIndexType


class Index(evaql_parserVisitor):
    def visitCreateIndex(self, ctx: evaql_parser.CreateIndexContext):
        # get relevant info from SQL Statement
        idx_name = ctx.uid(0).getText()
        idx_type = ctx.uid(1)
        table_info = self.visitTableName(ctx.tableName())
        table_ref = TableRef(table_info)

        # Figure out the column (UDF) on which user want to cerate an index.
        idx_col_names = ctx.indexColumnNames()
        if idx_col_names:
            idx_columns = self.visitIndexColumnNames(ctx.indexColumnNames())
        # If user didn't provide a column name (UDF name), use `FeatureExtractor` UDF as default.
        else:
            extractor_func = FunctionExpression(None, "FeatureExtractor")
            extractor_func.append_child(TupleValueExpression(col_name="data"))
            idx_columns = [extractor_func]

        if len(idx_columns) > 1:
            raise NotImplementedError("Currently CREATE INDEX doesn't"
                " support create index on multiple columns at one time.")

        faiss_idx_type = None

        if idx_type is not None:
            idx_type_text = idx_type.getText()
            if idx_type_text == "FlatL2":
                faiss_idx_type = FaissIndexType.FlatL2
            elif idx_type_text == "IVFFlat":
                faiss_idx_type = FaissIndexType.IVFFlat
            elif idx_type_text == "FlatIP":
                faiss_idx_type = FaissIndexType.FlatIP
            else:
                raise NotImplementedError(f"{idx_type_text} index type is not supported for now.")
        else:
            faiss_idx_type = FaissIndexType.FlatL2

        return CreateIndexStatement(idx_name, True, table_ref, idx_columns, faiss_idx_type)


    def visitIndexColumnNames(self, ctx: evaql_parser.IndexColumnNamesContext):
        cols = []
        for col in ctx.getChildren():
            if isinstance(col, evaql_parser.IndexColumnNameContext):
                cols.append(self.visitIndexColumnName(col))

        return cols

    def visitIndexColumnName(self, ctx: evaql_parser.IndexColumnNameContext):
        func = ctx.udfFunction()
        if func is not None:
            return self.visitUdfFunction(func)
        else:
            raise NotImplementedError()