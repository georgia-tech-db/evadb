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
import os
import tempfile

from src.utils.logging_manager import LoggingManager

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.planner.insert_plan import InsertPlan
from src.parser.table_ref import TableRef, TableInfo
from src.catalog.models.df_column import DataFrameColumn
from src.storage.dataframe import load_dataframe
from src.catalog.column_type import ColumnType
from src.executor.plan_executor import PlanExecutor
from src.optimizer.plan_generator import PlanGenerator
from src.utils.logging_manager import LoggingManager, LoggingLevel


@asyncio.coroutine
def handle_request(transport, query):
    """
        Reads a request from a client and processes it

        If user inputs 'quit' stops the event loop
        otherwise just echoes user input
    """
    parser = Parser()

    eva_statement = parser.parse(query)
    for i in range(len(eva_statement)):
        

        LoggingManager().log("Result from the parser: "+str(eva_statement[i]))
        
        logical_plan = StatementToPlanConvertor().visit(eva_statement[i])
        physical_plan = PlanGenerator().build(logical_plan)
        
        PlanExecutor(physical_plan).execute_plan()

    table_name = 'MyVideo'
    file_url = os.path.join(tempfile.gettempdir(), table_name)
    file_url = 'file://' + file_url
        
    df = load_dataframe(file_url)
    
    response_message = ','.join(map(str,df.collect()))

    LoggingManager().log("Response received" +str(response_message))

    LoggingManager().log('Response to client: --|' +
                         str(response_message) +
                         '|--')

    data = response_message.encode('ascii')
    transport.write(data)

    return response_message