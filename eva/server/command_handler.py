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
import asyncio
from typing import Iterator, Optional

from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.executor.plan_executor import PlanExecutor
from eva.models.server.response import Response, ResponseStatus
from eva.models.storage.batch import Batch
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from eva.parser.parser import Parser
from eva.server.networking_utils import serialize_message
from eva.utils.logging_manager import logger
from eva.utils.timer import Timer


def execute_query(query, report_time: bool = False) -> Iterator[Batch]:
    """
    Execute the query and return a result generator.
    """

    query_compile_time = Timer()
    with query_compile_time:
        stmt = Parser().parse(query)[0]
        StatementBinder(StatementBinderContext()).bind(stmt)
        l_plan = StatementToPlanConvertor().visit(stmt)
        p_plan = PlanGenerator().build(l_plan)
        output = PlanExecutor(p_plan).execute_plan()

    query_compile_time.log_elapsed_time("Query Compile Time")
    return output


def execute_query_fetch_all(query) -> Optional[Batch]:
    """
    Execute the query and fetch all results into one Batch object.
    """
    output = execute_query(query, report_time=True)
    if output:
        batch_list = list(output)
        return Batch.concat(batch_list, copy=False)


@asyncio.coroutine
def handle_request(transport, request_message):
    """
    Reads a request from a client and processes it

    If user inputs 'quit' stops the event loop
    otherwise just echoes user input
    """
    logger.debug("Receive request: --|" + str(request_message) + "|--")

    error = False
    error_msg = None
    query_runtime = Timer()
    with query_runtime:
        try:
            output_batch = execute_query_fetch_all(request_message)
        except Exception as e:
            error_msg = str(e)
            logger.warn(error_msg)
            error = True

    if not error:
        response = Response(
            status=ResponseStatus.SUCCESS,
            batch=output_batch,
            query_time=query_runtime.total_elapsed_time,
        )
    else:
        response = Response(
            status=ResponseStatus.FAIL,
            batch=None,
            error=error_msg,
        )

    query_runtime.log_elapsed_time("Query Response Time")

    responseData = serialize_message(response)

    transport.write(responseData)

    return response
