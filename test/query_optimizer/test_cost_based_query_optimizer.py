import src.constants as constants
from src.catalog.catalog import Catalog
from src.expression.abstract_expression import AbstractExpression, ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import LogicalExpression
from src.query_optimizer.pp_optmizer import *


def test_one():

    const_exp_01 = ConstantValueExpression("t")
    const_exp_02 = ConstantValueExpression("suv")
    cmpr_exp1 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_01, const_exp_02)

    const_exp_11 = ConstantValueExpression("c")
    const_exp_12 = ConstantValueExpression("white")
    cmpr_exp2 = ComparisonExpression(ExpressionType.COMPARE_EQUAL, const_exp_11, const_exp_12)

    const_exp_21 = ConstantValueExpression("c")
    const_exp_22 = ConstantValueExpression("white")
    cmpr_exp3 = ComparisonExpression(ExpressionType.COMPARE_NOT_EQUAL, const_exp_21, const_exp_22)

    logical_expr1 = LogicalExpression(cmpr_exp1, 'AND', cmpr_exp2)
    logical_expr2 = LogicalExpression(cmpr_exp1, 'AND', cmpr_exp3)

    catalog= Catalog(constants.UADETRAC)
    predicates = [logical_expr2]
    pp_optimizer = PPOptmizer(catalog, predicates)
    out = pp_optimizer.execute()


def test_return_same_query():
    query = "t=suv"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['t=suv']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = []

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_return_number_same_query():
    query = "s>60"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['s>60']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = []

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_simple_string_query():
    query = "c!=white"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['c=red', 'c=black', 'c=silver']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and, np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_or_query():
    query = "t=sedan || t=truck"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['t=sedan', 't=truck']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_or]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_numeric_query():
    query = "i=pt335 || i=pt342 && o!=pt211 && o!=pt208"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['i!=pt342', 'i!=pt211', 'i!=pt208', 'i!=pt335', 'i!=pt211', 'i!=pt208', 'o=pt335',
                              'o=pt342', 'o=pt208', 'o=pt335', 'o=pt342', 'o=pt211']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_or, np.logical_and, np.logical_and,
                                  np.logical_and, np.logical_and, np.logical_and, np.logical_and, np.logical_and,
                                  np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_simple_color_type_query():
    query = "t=suv && c!=white"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['t=suv', 'c=red', 'c=black', 'c=silver']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_complex_color_type_query():
    query = "t!=suv && t!=van && c!=red && t!=white"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['t!=suv', 't!=van', 'c=white', 'c=black', 'c=silver', 't=sedan', 't=suv', 't=truck',
                              't=van']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and, np.logical_and, np.logical_and, np.logical_and, np.logical_and,
                                  np.logical_and, np.logical_and, np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_medium_number_query():
    query = "s>60 && s<65"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['s>60', 's<70']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"


def test_mix_numeric_category_query():
    query = "t=van && s>60 && s<65"
    qo = CostBasedQueryOptimizer()
    optimal_query = qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    if optimal_query is None:
        assert False, "There was no optimal query returned"

    expected_optimal_query = ['t=van', 's>60', 's<70']

    if expected_optimal_query != optimal_query[0][0]:
        assert False, "The generated optimal predicates are wrong"

    expected_optimal_operators = [np.logical_and, np.logical_and]

    if expected_optimal_operators != optimal_query[0][1]:
        assert False, "The generated optimal predicates are wrong"
