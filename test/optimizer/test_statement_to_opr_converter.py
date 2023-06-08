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
import unittest
from inspect import signature
from test.util import get_all_subclasses

from mock import MagicMock, patch

from evadb.optimizer.operators import (
    Dummy,
    LogicalApplyAndMerge,
    LogicalCreate,
    LogicalCreateIndex,
    LogicalCreateMaterializedView,
    LogicalCreateUDF,
    LogicalDelete,
    LogicalDropObject,
    LogicalExchange,
    LogicalExplain,
    LogicalExtractObject,
    LogicalFilter,
    LogicalFunctionScan,
    LogicalGet,
    LogicalGroupBy,
    LogicalInsert,
    LogicalJoin,
    LogicalLimit,
    LogicalLoadData,
    LogicalOrderBy,
    LogicalProject,
    LogicalQueryDerivedGet,
    LogicalRename,
    LogicalSample,
    LogicalShow,
    LogicalUnion,
    LogicalVectorIndexScan,
    Operator,
)
from evadb.optimizer.statement_to_opr_converter import StatementToPlanConverter
from evadb.parser.create_index_statement import CreateIndexStatement
from evadb.parser.create_statement import CreateTableStatement
from evadb.parser.create_udf_statement import CreateUDFStatement
from evadb.parser.drop_object_statement import DropObjectStatement
from evadb.parser.explain_statement import ExplainStatement
from evadb.parser.insert_statement import InsertTableStatement
from evadb.parser.rename_statement import RenameTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.table_ref import TableRef


class StatementToOprTest(unittest.TestCase):
    @patch("evadb.optimizer.statement_to_opr_converter.LogicalGet")
    def test_visit_table_ref_should_create_logical_get_opr(self, mock_lget):
        converter = StatementToPlanConverter()
        table_ref = MagicMock(spec=TableRef, alias="alias")
        table_ref.is_select.return_value = False
        table_ref.sample_freq = None
        converter.visit_table_ref(table_ref)
        mock_lget.assert_called_with(table_ref, table_ref.table.table_obj, "alias")
        self.assertEqual(mock_lget.return_value, converter._plan)

    @patch("evadb.optimizer.statement_to_opr_converter.LogicalFilter")
    def test_visit_select_predicate_should_add_logical_filter(self, mock_lfilter):
        converter = StatementToPlanConverter()
        select_predicate = MagicMock()
        converter._visit_select_predicate(select_predicate)

        mock_lfilter.assert_called_with(select_predicate)
        mock_lfilter.return_value.append_child.assert_called()
        self.assertEqual(mock_lfilter.return_value, converter._plan)

    @patch("evadb.optimizer.statement_to_opr_converter.LogicalProject")
    def test_visit_projection_should_add_logical_predicate(self, mock_lproject):
        converter = StatementToPlanConverter()
        projects = MagicMock()

        converter._visit_projection(projects)
        mock_lproject.assert_called_with(projects)
        mock_lproject.return_value.append_child.assert_called()
        self.assertEqual(mock_lproject.return_value, converter._plan)

    def test_visit_select_should_call_appropriate_visit_methods(self):
        converter = StatementToPlanConverter()
        converter.visit_table_ref = MagicMock()
        converter._visit_projection = MagicMock()
        converter._visit_select_predicate = MagicMock()
        converter._visit_union = MagicMock()

        statement = MagicMock()
        statement.from_table = MagicMock(spec=TableRef)
        converter.visit_select(statement)

        converter.visit_table_ref.assert_called_with(statement.from_table)
        converter._visit_projection.assert_called_with(statement.target_list)
        converter._visit_select_predicate.assert_called_with(statement.where_clause)

    def test_visit_select_should_not_call_visits_for_null_values(self):
        converter = StatementToPlanConverter()
        converter.visit_table_ref = MagicMock()
        converter._visit_projection = MagicMock()
        converter._visit_select_predicate = MagicMock()
        converter._visit_union = MagicMock()

        statement = SelectStatement()

        converter.visit_select(statement)

        converter.visit_table_ref.assert_not_called()
        converter._visit_projection.assert_not_called()
        converter._visit_select_predicate.assert_not_called()

    @patch("evadb.optimizer.statement_to_opr_converter.LogicalCreateUDF")
    @patch(
        "evadb.optimizer.\
statement_to_opr_converter.column_definition_to_udf_io"
    )
    @patch(
        "evadb.optimizer.\
statement_to_opr_converter.metadata_definition_to_udf_metadata"
    )
    def test_visit_create_udf(self, metadata_def_mock, col_def_mock, l_create_udf_mock):
        converter = StatementToPlanConverter()
        stmt = MagicMock()
        stmt.name = "name"
        stmt.if_not_exists = True
        stmt.inputs = ["inp"]
        stmt.outputs = ["out"]
        stmt.impl_path = "tmp.py"
        stmt.udf_type = "classification"
        stmt.metadata = [("key1", "value1"), ("key2", "value2")]
        col_def_mock.side_effect = ["inp", "out"]
        metadata_def_mock.side_effect = [{"key1": "value1", "key2": "value2"}]
        converter.visit_create_udf(stmt)
        col_def_mock.assert_any_call(stmt.inputs, True)
        col_def_mock.assert_any_call(stmt.outputs, False)
        metadata_def_mock.assert_any_call(stmt.metadata)
        l_create_udf_mock.assert_called_once()
        l_create_udf_mock.assert_called_with(
            stmt.name,
            stmt.if_not_exists,
            "inp",
            "out",
            stmt.impl_path,
            stmt.udf_type,
            {"key1": "value1", "key2": "value2"},
        )

    def test_visit_should_call_create_udf(self):
        stmt = MagicMock(spec=CreateUDFStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_create_udf = mock

        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    @patch("evadb.optimizer.statement_to_opr_converter.LogicalDropObject")
    def test_visit_drop_object(self, l_drop_obj_mock):
        converter = StatementToPlanConverter()
        stmt = MagicMock()
        stmt.name = "name"
        stmt.object_type = "object_type"
        stmt.if_exists = True
        converter.visit_drop_object(stmt)
        l_drop_obj_mock.assert_called_once()
        l_drop_obj_mock.assert_called_with(stmt.object_type, stmt.name, stmt.if_exists)

    def test_visit_should_call_insert(self):
        stmt = MagicMock(spec=InsertTableStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_insert = mock

        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_create(self):
        stmt = MagicMock(spec=CreateTableStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_create = mock

        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_rename(self):
        stmt = MagicMock(spec=RenameTableStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_rename = mock

        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_explain(self):
        stmt = MagicMock(spec=ExplainStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_explain = mock

        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_once_with(stmt)

    def test_visit_should_call_drop(self):
        stmt = MagicMock(spec=DropObjectStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_drop_object = mock
        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_create_index(self):
        stmt = MagicMock(spec=CreateIndexStatement)
        converter = StatementToPlanConverter()
        mock = MagicMock()
        converter.visit_create_index = mock
        converter.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_inequality_in_operator(self):
        dummy_plan = Dummy(MagicMock(), MagicMock())
        object = MagicMock()
        self.assertNotEqual(dummy_plan, object)

    def test_check_plan_equality(self):
        plans = []
        dummy_plan = Dummy(MagicMock(), MagicMock())
        create_plan = LogicalCreate(MagicMock(), MagicMock())
        create_udf_plan = LogicalCreateUDF(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        create_index_plan = LogicalCreateIndex(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        create_materialized_view_plan = LogicalCreateMaterializedView(
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        delete_plan = LogicalDelete(MagicMock())
        insert_plan = LogicalInsert(
            MagicMock(), MagicMock(), [MagicMock()], [MagicMock()]
        )
        query_derived_plan = LogicalQueryDerivedGet(MagicMock())
        load_plan = LogicalLoadData(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        limit_plan = LogicalLimit(MagicMock())
        rename_plan = LogicalRename(MagicMock(), MagicMock())

        explain_plan = LogicalExplain([MagicMock()])
        exchange_plan = LogicalExchange(MagicMock())
        show_plan = LogicalShow(MagicMock())
        drop_plan = LogicalDropObject(MagicMock(), MagicMock(), MagicMock())
        get_plan = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        sample_plan = LogicalSample(MagicMock(), MagicMock())
        filter_plan = LogicalFilter(MagicMock())
        faiss_plan = LogicalVectorIndexScan(
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        groupby_plan = LogicalGroupBy(MagicMock())
        order_by_plan = LogicalOrderBy(MagicMock())
        union_plan = LogicalUnion(MagicMock())
        function_scan_plan = LogicalFunctionScan(MagicMock(), MagicMock())
        join_plan = LogicalJoin(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        project_plan = LogicalProject(MagicMock(), MagicMock())
        apply_and_merge_plan = LogicalApplyAndMerge(MagicMock(), MagicMock())
        extract_object_plan = LogicalExtractObject(
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        create_plan.append_child(create_udf_plan)

        plans.append(dummy_plan)
        plans.append(create_plan)
        plans.append(create_udf_plan)
        plans.append(create_index_plan)
        plans.append(create_materialized_view_plan)
        plans.append(delete_plan)
        plans.append(insert_plan)
        plans.append(query_derived_plan)
        plans.append(load_plan)
        plans.append(limit_plan)
        plans.append(rename_plan)
        plans.append(drop_plan)
        plans.append(get_plan)
        plans.append(sample_plan)
        plans.append(filter_plan)
        plans.append(groupby_plan)
        plans.append(order_by_plan)
        plans.append(union_plan)
        plans.append(function_scan_plan)
        plans.append(join_plan)
        plans.append(apply_and_merge_plan)
        plans.append(show_plan)
        plans.append(explain_plan)
        plans.append(exchange_plan)
        plans.append(faiss_plan)
        plans.append(project_plan)
        plans.append(extract_object_plan)

        derived_operators = list(get_all_subclasses(Operator))

        plan_type_list = []
        for plan in plans:
            plan_type_list.append(type(plan))

        length = len(plans)
        self.assertEqual(length, len(derived_operators))
        self.assertEqual(len(list(set(derived_operators) - set(plan_type_list))), 0)

        for i in range(length):
            self.assertEqual(plans[i], plans[i])
            self.assertNotEqual(str(plans[i]), None)
            # compare against dummy plan
            if plans[i] != dummy_plan:
                self.assertNotEqual(plans[i], dummy_plan)
            # compare against next plan
            if i >= 1:
                self.assertNotEqual(plans[i - 1], plans[i])

        derived_operators = list(get_all_subclasses(Operator))

        for derived_operator in derived_operators:
            sig = signature(derived_operator.__init__)
            params = sig.parameters
            self.assertLess(len(params), 10)
