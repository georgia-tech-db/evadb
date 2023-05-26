import asyncio
from typing import List
from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.executor.plan_executor import PlanExecutor
from eva.models.storage.batch import Batch
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.statement_to_opr_converter import StatementToPlanConverter
from eva.parser.statement import AbstractStatement

from eva.parser.utils import parse_expression


def string_list_to_expression_list(exprs: List[str]):
    return [parse_expression(expr) for expr in exprs]


def execute_statement(statement: AbstractStatement) -> Batch:
    StatementBinder(StatementBinderContext()).bind(statement)
    l_plan = StatementToPlanConverter().visit(statement)
    p_plan = asyncio.run(PlanGenerator().build(l_plan))
    output = PlanExecutor(p_plan).execute_plan()
    if output:
        batch_list = list(output)
        return Batch.concat(batch_list, copy=False)
