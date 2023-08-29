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
from typing import Union

import pandas

from evadb.database import EvaDBDatabase
from evadb.interfaces.relational.utils import (
    create_limit_expression,
    create_star_expression,
    handle_select_clause,
    sql_predicate_to_expresssion_tree,
    sql_string_to_expresssion_list,
    string_to_lateral_join,
    try_binding,
)
from evadb.models.storage.batch import Batch
from evadb.parser.alias import Alias
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import JoinNode, TableRef
from evadb.parser.types import JoinType
from evadb.parser.utils import parse_sql_orderby_expr
from evadb.server.command_handler import execute_statement


class EvaDBQuery:
    def __init__(
        self,
        evadb: EvaDBDatabase,
        query_node: Union[AbstractStatement, TableRef],
        alias: Alias = None,
    ):
        self._evadb = evadb
        self._query_node = query_node
        self._alias = alias

    def alias(self, alias: str) -> "EvaDBQuery":
        """Returns a new Relation with an alias set.

        Args:
            alias (str): an alias name to be set for the Relation.

        Returns:
            EvaDBQuery: Aliased Relation.

        Examples:
            >>> relation = cursor.table("sample_table")
            >>> relation.alias('table')
        """
        self._alias = Alias(alias)

    def cross_apply(self, expr: str, alias: str) -> "EvaDBQuery":
        """Execute a expr on all the rows of the relation

        Args:
            expr (str): sql expression
            alias (str): alias of the output of the expr

        Returns:
            `EvaDBQuery`: relation

        Examples:

            Runs Yolo on all the frames of the input table

            >>> relation = cursor.table("videos")
            >>> relation.cross_apply("Yolo(data)", "objs(labels, bboxes, scores)")

            Runs Yolo on all the frames of the input table and unnest each object as separate row.

            >>> relation.cross_apply("unnest(Yolo(data))", "obj(label, bbox, score)")
        """
        assert self._query_node.from_table is not None

        table_ref = string_to_lateral_join(expr, alias=alias)
        join_table = TableRef(
            JoinNode(
                TableRef(self._query_node, alias=self._alias),
                table_ref,
                join_type=JoinType.LATERAL_JOIN,
            )
        )
        self._query_node = SelectStatement(
            target_list=create_star_expression(), from_table=join_table
        )
        # reset the alias as after join there isn't a single alias
        self._alias = Alias("Relation")
        try_binding(self._evadb.catalog, self._query_node)
        return self

    def df(self) -> pandas.DataFrame:
        """Execute and fetch all rows as a pandas DataFrame

        Returns:
            pandas.DataFrame:
        """
        batch = self.execute()
        assert batch is not None, "relation execute failed"
        return batch.frames

    def execute(self) -> Batch:
        """Transform the relation into a result set

        Returns:
            Batch: result as evadb Batch
        """
        result = execute_statement(self._evadb, self._query_node.copy())
        assert result.frames is not None
        return result

    def filter(self, expr: str) -> "EvaDBQuery":
        """
        Filters rows using the given condition. Multiple filters can be chained using `AND`

        Parameters:
            expr (str): The filter expression.

        Returns:
            EvaDBQuery : Filtered EvaDBQuery.
        Examples:
            >>> relation = cursor.table("sample_table")
            >>> relation.filter("col1 > 10")

            Filter by sql string

            >>> relation.filter("col1 > 10 AND col1 < 20")

        """
        parsed_expr = sql_predicate_to_expresssion_tree(expr)

        self._query_node = handle_select_clause(
            self._query_node, self._alias, "where_clause", parsed_expr
        )

        try_binding(self._evadb.catalog, self._query_node)

        return self

    def limit(self, num: int) -> "EvaDBQuery":
        """Limits the result count to the number specified.

        Args:
            num (int): Number of records to return. Will return num records or all records if the Relation contains fewer records.

        Returns:
            EvaDBQuery: Relation with subset of records

        Examples:
            >>> relation = cursor.table("sample_table")
            >>> relation.limit(10)

        """

        limit_expr = create_limit_expression(num)
        self._query_node = handle_select_clause(
            self._query_node, self._alias, "limit_count", limit_expr
        )

        try_binding(self._evadb.catalog, self._query_node)

        return self

    def order(self, order_expr: str) -> "EvaDBQuery":
        """Reorder the relation based on the order_expr

        Args:
            order_expr (str): sql expression to order the relation

        Returns:
            EvaDBQuery: A EvaDBQuery ordered based on the order_expr.

        Examples:
            >>> relation = cursor.table("PDFs")
            >>> relation.order("Similarity(SentenceTransformerFeatureExtractor('When was the NATO created?'), SentenceTransformerFeatureExtractor(data) ) DESC")

        """

        parsed_expr = parse_sql_orderby_expr(order_expr)
        self._query_node = handle_select_clause(
            self._query_node, self._alias, "orderby_list", parsed_expr
        )

        try_binding(self._evadb.catalog, self._query_node)

        return self

    def select(self, expr: str) -> "EvaDBQuery":
        """
        Projects a set of expressions and returns a new EvaDBQuery.

        Parameters:
            exprs (Union[str, List[str]]): The expression(s) to be selected. If '*' is provided, it expands to all columns in the current EvaDBQuery.

        Returns:
            EvaDBQuery: A EvaDBQuery with subset (or all) of columns.

        Examples:
            >>> relation = cursor.table("sample_table")

            Select all columns in the EvaDBQuery.

            >>> relation.select("*")

            Select all subset of columns in the EvaDBQuery.

            >>> relation.select("col1")
            >>> relation.select("col1, col2")
        """

        parsed_exprs = sql_string_to_expresssion_list(expr)

        self._query_node = handle_select_clause(
            self._query_node, self._alias, "target_list", parsed_exprs
        )

        try_binding(self._evadb.catalog, self._query_node)

        return self

    def show(self) -> pandas.DataFrame:
        """Execute and fetch all rows as a pandas DataFrame

        Returns:
            pandas.DataFrame:
        """
        batch = self.execute()
        assert batch is not None, "relation execute failed"
        return batch.frames

    def sql_query(self) -> str:
        """Get the SQL query that is equivalent to the relation

        Returns:
            str: the sql query

        Examples:
            >>> relation = cursor.table("sample_table").project('i')
            >>> relation.sql_query()
        """

        return str(self._query_node)
