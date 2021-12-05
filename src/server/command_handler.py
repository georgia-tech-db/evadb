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
from typing import Iterator, Optional

import pandas as pd

from src.executor.plan_executor import PlanExecutor
from src.models.server.response import ResponseStatus, Response
from src.models.storage.batch import Batch
from src.optimizer.plan_generator import PlanGenerator
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.parser.parser import Parser
from src.utils.logging_manager import LoggingManager, LoggingLevel
from src.utils.metrics import MetricsManager, mm_start, mm_end, mm_end_start


def execute_query(query, mm: MetricsManager) -> Iterator[Batch]:
    """
    Execute the query and return a result generator.
    """
    mm_start(mm, "parsing")
    stmt = Parser().parse(query)[0]

    mm_end_start(mm, "parsing", "planning")
    l_plan = StatementToPlanConvertor().visit(stmt)
    p_plan = PlanGenerator().build(l_plan)

    mm_end_start(mm, "planning", "execution")
    output = PlanExecutor(p_plan).execute_plan()

    mm_end(mm, "execution")
    return output


def execute_query_fetch_all(query, mm: MetricsManager = None) -> Optional[
        Batch]:
    """
    Execute the query and fetch all results into one Batch object.
    """
    output = execute_query(query, mm)
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
    LoggingManager().log('Receive request: --|' + str(request_message) + '|--')

    mm = MetricsManager()

    try:
        output_batch = execute_query_fetch_all(request_message, mm)
    except Exception as e:
        LoggingManager().log(e, LoggingLevel.WARNING)
        output_batch = Batch(pd.DataFrame([{'error': str(e)}]))
        response = Response(status=ResponseStatus.FAIL, batch=output_batch)
    else:
        response = Response(status=ResponseStatus.SUCCESS,
                            batch=output_batch, metrics=mm.print())

    responseData = response.to_json()
    # Send data length, because response can be very large
    data = (str(len(responseData)) + '|' + responseData).encode('ascii')

    LoggingManager().log('Response to client: --|' +
                         str(response) + '|--\n' +
                         'Length: ' + str(len(responseData)))

    transport.write(data)

    return response
