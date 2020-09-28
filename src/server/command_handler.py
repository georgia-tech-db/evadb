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

import time
import asyncio

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.optimizer.plan_generator import PlanGenerator
from src.executor.plan_executor import PlanExecutor
from src.models.server.response import ResponseStatus, Response

from src.utils.logging_manager import LoggingManager, LoggingLevel


@asyncio.coroutine
def handle_request(transport, request_message):
    """
        Reads a request from a client and processes it

        If user inputs 'quit' stops the event loop
        otherwise just echoes user input
    """
    LoggingManager().log('Receive request: --|' + str(request_message) + '|--')

    output_batch = None
    response = None
    start_time = time.perf_counter()
    try:
        stmt = Parser().parse(request_message)[0]
        l_plan = StatementToPlanConvertor().visit(stmt)
        p_plan = PlanGenerator().build(l_plan)
        output_batch = PlanExecutor(p_plan).execute_plan()
    except Exception as e:
        LoggingManager().log(e, LoggingLevel.WARNING)
        response = Response(status=ResponseStatus.FAIL, batch=None)

    end_time = time.perf_counter()
    run_time = end_time - start_time
    if response is None:
        response = Response(status=ResponseStatus.SUCCESS,
                            batch=output_batch,
                            metrics={"latency": run_time})

    responseData = response.to_json()
    # Send data length, because response can be very large
    data = (str(len(responseData)) + '|' + responseData).encode('ascii')

    LoggingManager().log('Response to client: --|' +
                         str(response) + '|--\n' +
                         'Length: ' + str(len(responseData)))

    transport.write(data)

    return response
