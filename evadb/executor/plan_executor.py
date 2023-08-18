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
from evadb.executor.apply_and_merge_executor import ApplyAndMergeExecutor
from evadb.executor.create_database_executor import CreateDatabaseExecutor
from evadb.executor.create_executor import CreateExecutor
from evadb.executor.create_index_executor import CreateIndexExecutor
from evadb.executor.create_udf_executor import CreateUDFExecutor
from evadb.executor.delete_executor import DeleteExecutor
from evadb.executor.drop_object_executor import DropObjectExecutor
from evadb.executor.exchange_executor import ExchangeExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.executor.explain_executor import ExplainExecutor
from evadb.executor.function_scan_executor import FunctionScanExecutor
from evadb.executor.groupby_executor import GroupByExecutor
from evadb.executor.hash_join_executor import HashJoinExecutor
from evadb.executor.insert_executor import InsertExecutor
from evadb.executor.join_build_executor import BuildJoinExecutor
from evadb.executor.lateral_join_executor import LateralJoinExecutor
from evadb.executor.limit_executor import LimitExecutor
from evadb.executor.load_executor import LoadDataExecutor
from evadb.executor.nested_loop_join_executor import NestedLoopJoinExecutor
from evadb.executor.orderby_executor import OrderByExecutor
from evadb.executor.pp_executor import PPExecutor
from evadb.executor.predicate_executor import PredicateExecutor
from evadb.executor.project_executor import ProjectExecutor
from evadb.executor.rename_executor import RenameExecutor
from evadb.executor.sample_executor import SampleExecutor
from evadb.executor.seq_scan_executor import SequentialScanExecutor
from evadb.executor.show_info_executor import ShowInfoExecutor
from evadb.executor.storage_executor import StorageExecutor
from evadb.executor.union_executor import UnionExecutor
from evadb.executor.use_executor import UseExecutor
from evadb.executor.vector_index_scan_executor import VectorIndexScanExecutor
from evadb.models.storage.batch import Batch
from evadb.parser.create_statement import CreateDatabaseStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.use_statement import UseStatement
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType
from evadb.utils.logging_manager import logger


class PlanExecutor:
    """
    This is an interface between plan tree and execution tree.
    We traverse the plan tree and build execution tree from it

    Arguments:
        plan (AbstractPlan): Physical plan tree which needs to be executed
        evadb (EvaDBDatabase): database to execute the query on
    """

    def __init__(self, evadb: EvaDBDatabase, plan: AbstractPlan):
        self._db = evadb
        self._plan = plan

    def _build_execution_tree(
        self, plan: Union[AbstractPlan, AbstractStatement]
    ) -> AbstractExecutor:
        """build the execution tree from plan tree

        Arguments:
            plan {AbstractPlan} -- Input Plan tree

        Returns:
            AbstractExecutor -- Compiled Execution tree
        """
        root = None
        if plan is None:
            return root

        # First handle cases when the plan is actually a parser statement
        if isinstance(plan, CreateDatabaseStatement):
            return CreateDatabaseExecutor(db=self._db, node=plan)
        elif isinstance(plan, UseStatement):
            return UseExecutor(db=self._db, node=plan)

        # Get plan node type
        plan_opr_type = plan.opr_type

        if plan_opr_type == PlanOprType.SEQUENTIAL_SCAN:
            executor_node = SequentialScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.UNION:
            executor_node = UnionExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.STORAGE_PLAN:
            executor_node = StorageExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.PP_FILTER:
            executor_node = PPExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE:
            executor_node = CreateExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.RENAME:
            executor_node = RenameExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.DROP_OBJECT:
            executor_node = DropObjectExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.INSERT:
            executor_node = InsertExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE_UDF:
            executor_node = CreateUDFExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LOAD_DATA:
            executor_node = LoadDataExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.GROUP_BY:
            executor_node = GroupByExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.ORDER_BY:
            executor_node = OrderByExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LIMIT:
            executor_node = LimitExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.SAMPLE:
            executor_node = SampleExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.NESTED_LOOP_JOIN:
            executor_node = NestedLoopJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LATERAL_JOIN:
            logger.warn(
                "LateralJoin Executor should not be part of the execution plan."
                "Please raise an issue with the current query. Thanks!"
            )
            executor_node = LateralJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.HASH_JOIN:
            executor_node = HashJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.HASH_BUILD:
            executor_node = BuildJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.FUNCTION_SCAN:
            executor_node = FunctionScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.EXCHANGE:
            executor_node = ExchangeExecutor(db=self._db, node=plan)
            inner_executor = self._build_execution_tree(plan.inner_plan)
            executor_node.build_inner_executor(inner_executor)
        elif plan_opr_type == PlanOprType.PROJECT:
            executor_node = ProjectExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.PREDICATE_FILTER:
            executor_node = PredicateExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.SHOW_INFO:
            executor_node = ShowInfoExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.EXPLAIN:
            executor_node = ExplainExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE_INDEX:
            executor_node = CreateIndexExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.APPLY_AND_MERGE:
            executor_node = ApplyAndMergeExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.VECTOR_INDEX_SCAN:
            executor_node = VectorIndexScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.DELETE:
            executor_node = DeleteExecutor(db=self._db, node=plan)

        # EXPLAIN does not need to build execution tree for its children
        if plan_opr_type != PlanOprType.EXPLAIN:
            # Build Executor Tree for children
            for children in plan.children:
                executor_node.append_child(self._build_execution_tree(children))

        return executor_node

    def execute_plan(
        self,
        do_not_raise_exceptions: bool = False,
        do_not_print_exceptions: bool = False,
    ) -> Iterator[Batch]:
        """execute the plan tree"""
        try:
            execution_tree = self._build_execution_tree(self._plan)
            output = execution_tree.exec()
            if output is not None:
                yield from output
        except Exception as e:
            if do_not_raise_exceptions is False:
                if do_not_print_exceptions is False:
                    logger.exception(str(e))
                raise ExecutorError(e)
