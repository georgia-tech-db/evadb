import asyncio
from typing import List
from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.executor.plan_executor import PlanExecutor
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.statement_to_opr_converter import StatementToPlanConverter
from eva.parser.statement import AbstractStatement

from eva.parser.utils import (
    parse_expression,
    parse_lateral_join,
    parse_predicate_expression,
)


def sql_string_to_expresssion_list(expr: str) -> List[AbstractExpression]:
    """Converts the sql expression to list of eva abstract expressions

    Args:
        expr (str): the expr to convert

    Returns:
        List[AbstractExpression]: list of eva abstract expressions

    """
    return parse_expression(expr)


def sql_predicate_to_expresssion_tree(expr: str) -> AbstractExpression:
    return parse_predicate_expression(expr)


def execute_statement(statement: AbstractStatement) -> Batch:
    StatementBinder(StatementBinderContext()).bind(statement)
    l_plan = StatementToPlanConverter().visit(statement)
    p_plan = asyncio.run(PlanGenerator().build(l_plan))
    output = PlanExecutor(p_plan).execute_plan()
    if output:
        batch_list = list(output)
        return Batch.concat(batch_list, copy=False)


def string_to_lateral_join(expr: str, alias: str):
    return parse_lateral_join(expr, alias)


def create_star_expression():
    return [TupleValueExpression(col_name="*")]


def create_limit_expression(num: int):
    return ConstantValueExpression(num)


def try_binding(stmt: AbstractStatement):
    StatementBinder(StatementBinderContext()).bind(stmt)
