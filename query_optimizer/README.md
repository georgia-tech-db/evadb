To run query optimizer, please run the following command:

The query optimizer now has object 
```bash
python query_optimizer.py
```


Unit tests related to `query_optimizer.py` are in `tests\query_optimizer_test_pytest.py`
Change the current working directory to unit tests directory:

```shell
(eva_35) galis-MBP:Eva gali$ cd query_optimizer/tests/
(eva_35) galis-MBP:tests gali$ pytest query_optimizer_test_pytest.py
================================== test session starts =================================
platform darwin -- Python 3.7.3, pytest-5.1.2, py-1.8.0, pluggy-0.13.0
rootdir: /Users/gali/Documents/GitHub/test_main/Eva/query_optimizer/tests
plugins: cov-2.7.1
collected 10 items                                                                                                                                                                                                                                                      

query_optimizer_test_pytest.py ..........                                         [100%]

================================== 10 passed in 0.17s ==================================
```


To run expression parser:
```
cd query_optimizer
python expr_parser.py
```

To run unit-tests for expression parser:
```bash
(eva_35) galis-MBP:gali$ cd query_optimizer
(eva_35) galis-MBP:query_optimizer gali$ pytest tests/expr_parser_test.py 
========================================================================================================================== test session starts ==========================================================================================================================
platform darwin -- Python 3.7.3, pytest-5.1.2, py-1.8.0, pluggy-0.13.0
rootdir: /Users/gali/Documents/GitHub/test_main/Eva/query_optimizer
plugins: cov-2.7.1
collected 6 items                                                                                                                                                                                                                                                       

tests/expr_parser_test.py ..
....                                                                                                                                                                                                                                  [100%]

=================================================== warnings summary ====================================================================
<unknown>:1
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_number_expression
  <unknown>:1: DeprecationWarning: invalid escape sequence \d

<unknown>:1
<unknown>:1
<unknown>:1
<unknown>:1
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_number_expression
tests/expr_parser_test.py::test_multiple_number_expression
tests/expr_parser_test.py::test_multiple_number_expression
tests/expr_parser_test.py::test_multiple_number_expression
  <unknown>:1: DeprecationWarning: invalid escape sequence \w

<unknown>:1
<unknown>:1
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_expression_parser
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_number_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_basic_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_string_expression
tests/expr_parser_test.py::test_multiple_number_expression
tests/expr_parser_test.py::test_multiple_number_expression
  <unknown>:1: DeprecationWarning: invalid escape sequence \s

-- Docs: https://docs.pytest.org/en/latest/warnings.html
================== 6 passed, 42 warnings in 0.15s =======================================================
```

