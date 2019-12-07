import unittest

from src.query_optimizer.pp_optmizer import *


class PredicateExecutorTest(unittest.TestCase):
    def test_one(self):
        const_exp_01 = ConstantValueExpression("t")
        const_exp_02 = ConstantValueExpression("suv")

        # t=suv
        cmpr_exp1 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_01, const_exp_02)

        # c=white
        const_exp_21 = ConstantValueExpression("c")
        const_exp_22 = ConstantValueExpression("white")
        cmpr_exp3 = ComparisonExpression(ExpressionType.COMPARE_NEQ, const_exp_21, const_exp_22)

        logical_expr2 = LogicalExpression(cmpr_exp1, ExpressionType.LOGICAL_AND, cmpr_exp3)

        catalog = Catalog(constants.UADETRAC)
        predicates = [logical_expr2]
        pp_optimizer = PPOptmizer(catalog, predicates)
        out = pp_optimizer.execute()
        self.assertIsNotNone(out, "Should not be none")

        # expected
        a = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_01, const_exp_02)

        const_exp_111 = ConstantValueExpression("c")
        const_exp_122 = ConstantValueExpression("red")
        red = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_111, const_exp_122)

        const_exp_1111 = ConstantValueExpression("c")
        const_exp_1222 = ConstantValueExpression("black")
        black = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_1111, const_exp_1222)

        child = LogicalExpression(red, ExpressionType.LOGICAL_AND, black)
        silver = ComparisonExpression(ExpressionType.COMPARE_EQUAL, ConstantValueExpression("c"),
                                      ConstantValueExpression("silver"))
        logical_expr3 = LogicalExpression(child, ExpressionType.LOGICAL_AND, silver)
        expected_result = LogicalExpression(a, ExpressionType.LOGICAL_AND, logical_expr3)

        self.assertEqual(out[0], expected_result)

    def test_return_same_query(self):
        const_exp_01 = ConstantValueExpression("t")
        const_exp_02 = ConstantValueExpression("suv")

        # t=suv
        cmpr_exp1 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_01, const_exp_02)
        child = LogicalExpression(cmpr_exp1, ExpressionType.LOGICAL_OR, None)


        catalog = Catalog(constants.UADETRAC)
        predicates = [child]
        pp_optimizer = PPOptmizer(catalog, predicates)
        out = pp_optimizer.execute()
        self.assertIsNotNone(out, "Should not be none")


        self.assertEqual(out[0], child)

# TODO(galipremsagar): Add the following tests.
# def test_return_number_same_query():
#     query = "s>60"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['s>60']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = []
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_simple_string_query():
#     query = "c!=white"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['c=red', 'c=black', 'c=silver']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and, np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_or_query():
#     query = "t=sedan || t=truck"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['t=sedan', 't=truck']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_or]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_numeric_query():
#     query = "i=pt335 || i=pt342 && o!=pt211 && o!=pt208"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['i!=pt342', 'i!=pt211', 'i!=pt208', 'i!=pt335', 'i!=pt211', 'i!=pt208', 'o=pt335',
#                               'o=pt342', 'o=pt208', 'o=pt335', 'o=pt342', 'o=pt211']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_or, np.logical_and, np.logical_and,
#                                   np.logical_and, np.logical_and, np.logical_and, np.logical_and, np.logical_and,
#                                   np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_simple_color_type_query():
#     query = "t=suv && c!=white"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['t=suv', 'c=red', 'c=black', 'c=silver']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_complex_color_type_query():
#     query = "t!=suv && t!=van && c!=red && t!=white"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['t!=suv', 't!=van', 'c=white', 'c=black', 'c=silver', 't=sedan', 't=suv', 't=truck',
#                               't=van']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_and, np.logical_and, np.logical_and,
#                                   np.logical_and, np.logical_and, np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_medium_number_query():
#     query = "s>60 && s<65"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['s>60', 's<70']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
#
#
# def test_mix_numeric_category_query():
#     query = "t=van && s>60 && s<65"
#     qo = CostBasedQueryOptimizer()
#     optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)
#
#     if optimal_query is None:
#         assert False, "There was no optimal query returned"
#
#     expected_optimal_query = ['t=van', 's>60', 's<70']
#
#     if expected_optimal_query != optimal_query[0][0]:
#         assert False, "The generated optimal predicates are wrong"
#
#     expected_optimal_operators = [np.logical_and, np.logical_and]
#
#     if expected_optimal_operators != optimal_query[0][1]:
#         assert False, "The generated optimal predicates are wrong"
