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

from src.utils.logging_manager import LoggingManager

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor

from src.executor.plan_executor import PlanExecutor
from src.optimizer.plan_generator import PlanGenerator
from src.utils.logging_manager import LoggingManager


@asyncio.coroutine
def handle_request(transport, query):
    """
       Handles the request from the client.
       It calls the eva backend to serve the query
       and returns the response back.
       `ToDo`: Handle input query errors and expections returned by eva backend
    """
    parser = Parser()
    eva_statements = parser.parse(query)
    eva_response_messages = []

    # ToDo: In case of multiple queries,
    # We should be able to serve query asap and not wait for all the queries
    # to execute.Handle cases where we encounter errors in intermediate query.
    # I think we should stop serving as soon as we find an erroneous query
    for statement in eva_statements:
        LoggingManager().log("Parse Tree: " + str(statement))
        logical_plan = StatementToPlanConvertor().visit(statement)
        physical_plan = PlanGenerator().build(logical_plan)
        df = PlanExecutor(physical_plan).execute_plan()
        statement_response_message = ','.join(map(str, df.collect()))
        eva_response_messages.append(statement_response_message)

    # ToDo: Investigate if asyncio supports list based message passing?
    # Else we have to reduce the list of responses to a single response
    response_message = '\n'.join(eva_response_messages)
    LoggingManager().log('Response to client: --|' +
                         str(response_message) +
                         '|--')

    data = response_message.encode('ascii')
    transport.write(data)

    return response_message
