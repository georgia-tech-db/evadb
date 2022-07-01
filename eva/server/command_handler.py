# coding=utf-8
# Copyright 2018-2020 EVA
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
import pandas as pd

from typing import Iterator, Optional
from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext

from eva.parser.parser import Parser
from eva.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from eva.optimizer.plan_generator import PlanGenerator
from eva.executor.plan_executor import PlanExecutor
from eva.models.server.response import ResponseStatus, Response
from eva.models.storage.batch import Batch
from eva.utils.logging_manager import logger


def execute_query(query) -> Iterator[Batch]:
    """
    Execute the query and return a result generator.
    """
    stmt = Parser().parse(query)[0]
    try:
        StatementBinder(StatementBinderContext()).bind(stmt)
    except Exception as error:
        raise RuntimeError(f'Binder failed: {error}')
    l_plan = StatementToPlanConvertor().visit(stmt)
    p_plan = PlanGenerator().build(l_plan)
    return PlanExecutor(p_plan).execute_plan()


def execute_query_fetch_all(query) -> Optional[Batch]:
    """
    Execute the query and fetch all results into one Batch object.
    """
    output = execute_query(query)
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
    logger.debug('Receive request: --|' + str(request_message) + '|--')

    try:
        output_batch = execute_query_fetch_all(request_message)
    except Exception as e:
        logger.warn(e)
        output_batch = Batch(pd.DataFrame([{'error': str(e)}]))
        response = Response(status=ResponseStatus.FAIL, batch=output_batch)
    else:
        response = Response(status=ResponseStatus.SUCCESS, batch=output_batch)

    responseData = response.to_json()
    # Send data length, because response can be very large
    data = (str(len(responseData)) + '|' + responseData).encode('ascii')

    logger.debug('Response to client: --|' +
                         str(response) + '|--\n' +
                         'Length: ' + str(len(responseData)))

    transport.write(data)

    return response
