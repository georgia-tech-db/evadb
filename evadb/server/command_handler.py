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
import asyncio
from typing import Iterator, Optional

from evadb.binder.statement_binder import StatementBinder
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.database import EvaDBDatabase
from evadb.executor.plan_executor import PlanExecutor
from evadb.models.server.response import Response, ResponseStatus
from evadb.models.storage.batch import Batch
from evadb.optimizer.plan_generator import PlanGenerator
from evadb.optimizer.statement_to_opr_converter import StatementToPlanConverter
from evadb.parser.parser import Parser
from evadb.utils.logging_manager import logger
from evadb.utils.stats import Timer


def execute_query(
    evadb: EvaDBDatabase, query, report_time: bool = False, **kwargs
) -> Iterator[Batch]:
    """
    Execute the query and return a result generator.
    """
    query_compile_time = Timer()
    plan_generator = kwargs.pop("plan_generator", PlanGenerator(evadb))
    with query_compile_time:
        stmt = Parser().parse(query)[0]
        StatementBinder(StatementBinderContext(evadb.catalog)).bind(stmt)
        l_plan = StatementToPlanConverter().visit(stmt)
        p_plan = asyncio.run(plan_generator.build(l_plan))
        output = PlanExecutor(evadb, p_plan).execute_plan()

    query_compile_time.log_elapsed_time("Query Compile Time")
    return output


def execute_query_fetch_all(
    evadb: EvaDBDatabase, query=None, **kwargs
) -> Optional[Batch]:
    """
    Execute the query and fetch all results into one Batch object.
    """
    output = execute_query(evadb, query, report_time=True, **kwargs)
    if output:
        batch_list = list(output)
        return Batch.concat(batch_list, copy=False)


async def handle_request(evadb: EvaDBDatabase, client_writer, request_message):
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
            output_batch = execute_query_fetch_all(evadb, request_message)
        except Exception as e:
            error_msg = str(e)
            logger.exception(error_msg)
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

    logger.debug(response)

    response_data = Response.serialize(response)

    client_writer.write(b"%d\n" % len(response_data))
    client_writer.write(response_data)

    return response
