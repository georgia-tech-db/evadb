import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.query_optimizer.query_optimizer import QueryOptimizer
except ImportError:
    sys.path.append(root)
    from src.query_optimizer.query_optimizer import QueryOptimizer

import json

import numpy as np

import constants
from query_optimizer.query_optimizer import CostBasedQueryOptimizer

synthetic_pp_list = ["t=suv", "t=van", "t=sedan", "t=truck",
                     "c=red", "c=white", "c=black", "c=silver",
                     "s>40", "s>50", "s>60", "s<65", "s<70",
                     "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                     "o=pt335", "o=pt211", "o=pt342", "o=pt208"]

with open('../utils/synthetic_pp_stats_short.json') as f1:
    synthetic_pp_stats_short = json.load(f1)

with open('../utils/synthetic_pp_stats.json') as f2:
    synthetic_pp_stats = json.load(f2)

label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
              "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
              "c": [constants.DISCRETE,
                    ["white", "red", "black", "silver"]],
              "i": [constants.DISCRETE,
                    ["pt335", "pt342", "pt211", "pt208"]],
              "o": [constants.DISCRETE,
                    ["pt335", "pt342", "pt211", "pt208"]]}


# TODO: Fix this test - THIS TEST IS GOING AWAY AS THIS IS PURELY STRING PARSER TESTCASE.
# def test_parseQuery():
#
#     #case 1: Simple input/ouput check
#     predicates,connectors=obj._parseQuery("t>60 && q>=4 && v=car")
#     if predicates!=[["t",">","60"],["q",">=","4"],["v","=","car"]]:
#         assert False,"Wrong breakdown of predicates"
#     if connectors!=["&&","&&"]:
#         assert False,"Wrong list of connectors"
#
#     # case 2: Case when an extra space is present in the input
#     predicates, connectors = obj._parseQuery("t>60  && q>=4 && v=car")
#     if predicates != [["t", ">", "60"], ["q", ">=", "4"], ["v", "=", "car"]]:
#         assert False, "Wrong breakdown of predicates, can't handle
#         consecutive spaces."
#     if connectors != ["&&", "&&"]:
#         assert False, "Wrong list of connectors"
#
#     #case 2: No operator exists
#     predicates, connectors = obj._parseQuery("t!60")
#     if predicates != []:
#         assert False, "Wrong breakdown of predicates"
#     if connectors != []:
#         assert False, "Wrong list of connectors"
#
#     predicates, connectors = obj._parseQuery("t>60 && adfsg")
#     if predicates != []:
#         assert False, "Wrong breakdown of predicates"
#     if connectors != []:
#         assert False, "Wrong list of connectors"
#
#     #case for >> and similar situations, the >> operator should be
#     recognised as >
#     predicates, connectors = obj._parseQuery("t>>60 && a<45")
#     print((predicates, connectors))
#     if predicates != [['t','>','60'],['a','<','45']]:
#         assert False, "Wrong breakdown of predicates,the >> operator should
#         be recognised as > and likewise for <"
#     if connectors != ['&&']:
#         assert False, "Wrong list of connectors"
#
#     #case 2: Check for ordering of execution based on parenthesis code does
#     not handle this yet so now way to test at the moment
#     predicates, connectors = obj._parseQuery("t>60||(q>=4&&v=car)")
#     if predicates != [["t", ">", "60"], ["q", ">=", "4"], ["v", "=", "car"]]:
#         assert False, "Wrong breakdown of predicates"
#     if connectors != ["&&", "&&"]:
#         assert False, "Wrong list of connectors"
#
#     assert True

def test_convertL2S():
    obj = CostBasedQueryOptimizer()
    query_string = obj.convertL2S(["t", "!=", "10"], [])
    if query_string != "t!=10":
        assert False, "Wrong output query string"
    assert True

    query_string = obj.convertL2S(
        [["t", "!=", "10"], ['a', '<', '5'], ['b', '=', '1003']], ["&&", "||"])
    if query_string != "t!=10 && a<5 || b=1003":
        assert False, "Wrong output query string"

    # case for paranthesis hasn't been implemented yet when its done need to
    # add test cases for that.
    # assert True


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
