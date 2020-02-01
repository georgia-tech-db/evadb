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
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.optimizer.query_optimizer import QueryOptimizer
except ImportError:
    sys.path.append(root)
    from src.optimizer.query_optimizer import QueryOptimizer

obj = QueryOptimizer()


# TODO: Fix this test
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


# test_parseQuery()
# test_convertL2S()
