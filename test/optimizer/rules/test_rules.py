import unittest

from mock import MagicMock

from eva.optimizer.operators import (LogicalGet, LogicalProject, LogicalFilter,
                                     LogicalQueryDerivedGet, LogicalSample,
                                     LogicalJoin,
                                     LogicalQueryDerivedGet,
                                     LogicalSample)
from eva.optimizer.rules.rules import (EmbedProjectIntoGet, EmbedFilterIntoGet,
                                       EmbedFilterIntoDerivedGet,
                                       EmbedProjectIntoDerivedGet,
                                       LogicalCreateMaterializedViewToPhysical,
                                       PushdownFilterThroughSample,
                                       PushdownProjectThroughSample,
                                       PushdownProjectThroughJoin,
                                       PushdownFilterThroughJoin,
                                       LogicalCreateToPhysical,
                                       LogicalCreateUDFToPhysical,
                                       LogicalInsertToPhysical,
                                       LogicalLoadToPhysical,
                                       LogicalUploadToPhysical,
                                       LogicalSampleToUniformSample,
                                       LogicalGetToSeqScan,
                                       LogicalDerivedGetToPhysical,
                                       LogicalUnionToPhysical,
                                       LogicalOrderByToPhysical,
                                       LogicalLimitToPhysical,
                                       LogicalFunctionScanToPhysical,
                                       LogicalJoinToPhysical)
from eva.optimizer.rules.rules import Promise, RulesManager


class TestRules(unittest.TestCase):

    def test_rules_promises_order(self):
        # Promise of all rewrite should be greater than implementation
        self.assertTrue(Promise.EMBED_FILTER_INTO_DERIVED_GET >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.EMBED_PROJECT_INTO_DERIVED_GET >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.PUSHDOWN_FILTER_THROUGH_SAMPLE >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.PUSHDOWN_PROJECT_THROUGH_SAMPLE >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.EMBED_FILTER_INTO_GET >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.EMBED_PROJECT_INTO_GET >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.PUSHDOWN_FILTER_THROUGH_JOIN >
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.PUSHDOWN_PROJECT_THROUGH_JOIN >
                        Promise.IMPLEMENTATION_DELIMETER)

        # Promise of implementation rules should be lesser than rewrite rules
        self.assertTrue(Promise.LOGICAL_CREATE_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_CREATE_UDF_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_GET_TO_SEQSCAN <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_INSERT_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_LIMIT_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_ORDERBY_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_SAMPLE_TO_UNIFORMSAMPLE <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_LOAD_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_UPLOAD_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_UNION_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)
        self.assertTrue(Promise.LOGICAL_JOIN_TO_PHYSICAL <
                        Promise.IMPLEMENTATION_DELIMETER)

    def test_supported_rules(self):
        # adding/removing rules should update this test
        supported_rewrite_rules = [EmbedFilterIntoGet(),
                                   EmbedFilterIntoDerivedGet(),
                                   PushdownFilterThroughSample(),
                                   PushdownFilterThroughJoin()
                                   ]
        self.assertEqual(len(supported_rewrite_rules),
                         len(RulesManager().rewrite_rules))
        # check all the rule instance exists
        for rule in supported_rewrite_rules:
            self.assertTrue(any(isinstance(rule, type(x))
                                for x in RulesManager().rewrite_rules))

        supported_implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalLoadToPhysical(),
            LogicalUploadToPhysical(),
            LogicalSampleToUniformSample(),
            LogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalFunctionScanToPhysical(),
            LogicalJoinToPhysical(),
            LogicalCreateMaterializedViewToPhysical()]
        self.assertEqual(len(supported_implementation_rules),
                         len(RulesManager().implementation_rules))

        for rule in supported_implementation_rules:
            self.assertTrue(any(isinstance(rule, type(x))
                                for x in RulesManager().implementation_rules))

    # EmbedProjectIntoGet
    def test_simple_project_into_get(self):
        rule = EmbedProjectIntoGet()
        expr1 = MagicMock()
        expr2 = MagicMock()
        expr3 = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock())
        logi_project = LogicalProject([expr1, expr2, expr3], [logi_get])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertFalse(rewrite_opr is logi_get)
        self.assertEqual(rewrite_opr.target_list, [expr1, expr2, expr3])

    # EmbedFilterIntoGet
    def test_simple_filter_into_get(self):
        rule = EmbedFilterIntoGet()
        predicate = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertFalse(rewrite_opr is logi_get)
        self.assertEqual(rewrite_opr.predicate, predicate)

    # EmbedFilterIntoDerivedGet
    def test_simple_filter_into_derived_get(self):
        rule = EmbedFilterIntoDerivedGet()
        predicate = MagicMock()

        logi_derived_get = LogicalQueryDerivedGet()
        logi_filter = LogicalFilter(predicate, [logi_derived_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertFalse(rewrite_opr is logi_derived_get)
        self.assertEqual(rewrite_opr.predicate, predicate)

    # EmbedProjectIntoDerivedGet
    def test_simple_project_into_derived_get(self):
        rule = EmbedProjectIntoDerivedGet()
        target_list = MagicMock()

        logi_derived_get = LogicalQueryDerivedGet()
        logi_project = LogicalProject(target_list, [logi_derived_get])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertFalse(rewrite_opr is logi_derived_get)
        self.assertEqual(rewrite_opr.target_list, target_list)

    # PushdownFilterThroughSample
    def test_pushdown_filter_thru_sample(self):
        rule = PushdownFilterThroughSample()
        predicate = MagicMock()
        constexpr = MagicMock()
        logi_get = LogicalGet(MagicMock(), MagicMock())
        sample = LogicalSample(constexpr, [logi_get])
        logi_filter = LogicalFilter(predicate, [sample])
        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertIsInstance(rewrite_opr, LogicalSample)
        print(rewrite_opr.children[0])
        self.assertIsInstance(rewrite_opr.children[0], LogicalFilter)
        self.assertIsInstance(rewrite_opr.children[0].children[0], LogicalGet)

    # PushdownProjectThroughSample
    def test_pushdown_project_thru_sample(self):
        rule = PushdownProjectThroughSample()
        target_list = MagicMock()
        constexpr = MagicMock()
        logi_get = LogicalGet(MagicMock(), MagicMock())
        sample = LogicalSample(constexpr, [logi_get])
        logi_project = LogicalProject(target_list, [sample])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertTrue(rewrite_opr is sample)
        self.assertFalse(rewrite_opr.children[0] is logi_project)
        self.assertTrue(logi_get is rewrite_opr.children[0].children[0])
        self.assertEqual(rewrite_opr.children[0].target_list, target_list)

    # PushdownFilterThroughJoin
    def test_pushdown_filter_thru_join(self):
        rule = PushdownFilterThroughJoin()
        predicate = MagicMock()

        logi_join = LogicalJoin(MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_join])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertEqual(rewrite_opr, logi_join)
        self.assertEqual(rewrite_opr.predicate, predicate)

    # PushdownProjectThroughJoin
    def PushdownProjectThroughJoin(self):
        rule = EmbedProjectIntoGet()
        expr1 = MagicMock()
        expr2 = MagicMock()
        expr3 = MagicMock()

        logi_join = LogicalJoin(MagicMock())
        logi_project = LogicalProject([expr1, expr2, expr3], [logi_join])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertEqual(rewrite_opr, logi_join)
        self.assertEqual(rewrite_opr.target_list, [expr1, expr2, expr3])
