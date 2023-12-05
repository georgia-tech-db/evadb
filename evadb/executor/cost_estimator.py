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
from typing import Iterator, Union

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.vector_index_scan_executor import VectorIndexScanExecutor
from evadb.models.storage.batch import Batch
from evadb.parser.create_statement import CreateDatabaseStatement
from evadb.parser.set_statement import SetStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.use_statement import UseStatement
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType
from evadb.utils.logging_manager import logger
from evadb.configuration import constants
import json
import ast


class CostEstimator:
    """
    This acts as the interface to estimate the cost of a particular query. Now it is implemeted after the query optimization
    stage, but ideally this will be present as part of optimization engine and help in deciding the right plan

    Arguments:
        plan (AbstractPlan): Physical plan tree which needs to be executed
        evadb (EvaDBDatabase): database to execute the query on
    """

    def __init__(self, evadb: EvaDBDatabase, plan: AbstractPlan):
        self._db = evadb
        self._plan = plan
        self._cost = 0
        self._predicateSet = []

    def getCostFromStats(self,table_name):
        if str(table_name) in self._predicateSet:
            return 0
        elif str(table_name) in constants.EVADB_STATS:
            table_data = constants.EVADB_STATS[str(table_name)]
            num_rows = table_data.get('num_rows',0)
            return num_rows
        else:
            return 0

    def _build_execution_tree(
        self, plan: Union[AbstractPlan, AbstractStatement]
    ) -> AbstractExecutor:
        
        root = None
        if plan is None:
            return root

        # First handle cases when the plan is actually a parser statement
        if isinstance(plan, CreateDatabaseStatement):
            self._cost += 0
        elif isinstance(plan, UseStatement):
            self._cost += 0
        elif isinstance(plan, SetStatement):
            self._cost += 0

        # Get plan node type
        plan_opr_type = plan.opr_type

        # Cost Estimation added for Seq Scan and Predicate Scan
        # TODO: Add cost estimations for other types of operators
        if plan_opr_type == PlanOprType.SEQUENTIAL_SCAN:
            self._cost += self.getCostFromStats(plan.alias)
        elif plan_opr_type == PlanOprType.UNION:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.STORAGE_PLAN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.PP_FILTER:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.CREATE:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.RENAME:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.DROP_OBJECT:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.INSERT:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.CREATE_FUNCTION:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.LOAD_DATA:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.GROUP_BY:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.ORDER_BY:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.LIMIT:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.SAMPLE:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.NESTED_LOOP_JOIN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.HASH_JOIN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.HASH_BUILD:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.FUNCTION_SCAN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.EXCHANGE:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.PROJECT:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.PREDICATE_FILTER:
            self.getCostFromPredicate(plan.predicate)
        elif plan_opr_type == PlanOprType.SHOW_INFO:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.EXPLAIN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.CREATE_INDEX:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.APPLY_AND_MERGE:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.VECTOR_INDEX_SCAN:
            self._cost += 0.0
        elif plan_opr_type == PlanOprType.DELETE:
            self._cost += 0.0

        for children in plan.children:
            self._build_execution_tree(children)

    def get_execution_cost(
        self,
        do_not_raise_exceptions: bool = False,
        do_not_print_exceptions: bool = False,
    ) -> Iterator[Batch]:
        """cost estimation of the plan tree"""
        try:
           self._build_execution_tree(self._plan)
           return self._cost
        except Exception as e:
            if do_not_raise_exceptions is False:
                if do_not_print_exceptions is False:
                    logger.exception(str(e))

    def getCostFromPredicate(self, plan_predicate):
        predicate = str(plan_predicate).split(" ")
        table_name = predicate[2].split(".")[0]
        column = predicate[2].split(".")[1]
        condition = predicate[3]
        condition_value =  predicate[4][:-1]
        self._predicateSet.append(table_name)
        if str(table_name) in constants.EVADB_STATS:
            table_data = constants.EVADB_STATS[str(table_name)]
            hist_data = table_data["hist"]
            my_list = ast.literal_eval(hist_data)
            json_data = json.dumps(my_list)
            data_list = json.loads(json_data)
            for item in data_list:
                level_dict = item.get(table_name + "." + column, {})
                for value in level_dict:
                    if self.evaluate(condition_value,condition,value):
                        self._cost += level_dict[value]


    def evaluate(self, condition_value, condition, value):
        if condition == '>':
            if value > condition_value:
                return True
            else:
                return False
        elif condition == '>=':
            if value >= condition_value:
                return True
            else:
                return False
        elif condition == '<':
            if value < condition_value:
                return True
            else:
                return False
        elif condition == '<=':
            if value <= condition_value:
                return True
            else:
                return False
        elif condition == '=':
            if value == condition_value:
                return True
            else:
                return False
        return False



