import pandas
from eva.expression.expression_utils import conjunction_list_to_expression_tree
from eva.interfaces.relational.utils import (
    execute_statement,
    sql_predicate_to_expresssion_tree,
    sql_string_to_expresssion_list,
    string_to_lateral_join,
)
from eva.models.storage.batch import Batch
from eva.parser.select_statement import SelectStatement

from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import JoinNode, TableRef
from eva.parser.types import JoinType


class EVARelation:
    def __init__(self, stmt: AbstractStatement):
        self._eva_statement: AbstractStatement = stmt

    def select(self, expr: str) -> "EVARelation":
        """
        Projects a set of expressions and returns a new EVARelation.

        Parameters:
            exprs (Union[str, List[str]]): The expression(s) to be selected.
            If `*` is provided, it expands to all columns in the current EVARelation.

        Returns:
            EVARelation: A EVARelation with subset (or all) of columns.

        Examples:
            >>> relation = conn.table("sample_table")

            Select all columns in the EVARelation.

            >>> relation.select("*")

            Select all subset of columns in the EVARelation.

            >>> relation.select("col1")
            >>> relation.select("col1, col2")
        """
        assert isinstance(self._eva_statement, SelectStatement)

        parsed_exprs = sql_string_to_expresssion_list(expr)

        self._eva_statement.target_list = parsed_exprs

        return self

    def filter(self, expr: str) -> "EVARelation":
        """
        Filters rows using the given condition. Multiple chained filters results in `AND`

        Parameters:
            expr (str): The filter expression.

        Returns:
            EVARelation : Filtered EVARelation.
        Examples:
            >>> relation = conn.table("sample_table")
            >>> relation.filter("col1 > 10")

            Filter by sql string

            >>> relation.filter("col1 > 10 AND col1 < 20")

            Multiple filters is equivalent to `AND`

            >>> relation.filter("col1 > 10").filter("col1 <20")
        """
        assert isinstance(self._eva_statement, SelectStatement)
        parsed_expr = sql_predicate_to_expresssion_tree(expr)

        if self._eva_statement.where_clause is None:
            self._eva_statement.where_clause = parsed_expr
        else:
            # AND the clause with the existing expression
            self._eva_statement.where_clause = conjunction_list_to_expression_tree(
                [self._eva_statement.where_clause, parsed_expr]
            )

        return self

    def execute(self) -> Batch:
        """Transform the relation into a result set

        Returns:
            Batch: result as eva Batch
        """
        result = execute_statement(self._eva_statement)
        assert result.frames is not None
        return result

    def df(self) -> pandas.DataFrame:
        """Execute and fetch all rows as a pandas DataFrame

        Returns:
            pandas.DataFrame:
        """
        batch = self.execute()
        assert batch is not None, "relation execute failed"
        return batch.frames

    def cross_apply(self, expr: str, alias: str) -> "EVARelation":
        """Execute a expr on all the rows of the relation

        Args:
            expr (str): sql expression
            alias (str): alias of the output of the expr

        Returns:
            EVARelation: relation

        Examples:

            Runs Yolo on all the frames of the input table

            >>> relation = conn.table("videos")
            >>> relation.cross_apply("Yolo(data)", "objs(labels, bboxes, scores)")

            Runs Yolo on all the frames of the input table and unnest each object as separate row.
            >>> relation.cross_apply("unnest(Yolo(data))", "obj(label, bbox, score)")
        """
        assert isinstance(self._eva_statement, SelectStatement)
        assert self._eva_statement.from_table is not None

        table_ref = string_to_lateral_join(expr, alias=alias)
        self._eva_statement.from_table = TableRef(
            JoinNode(
                self._eva_statement.from_table,
                table_ref,
                join_type=JoinType.LATERAL_JOIN,
            )
        )
        return self
