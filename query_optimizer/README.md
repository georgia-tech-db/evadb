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
```
cd query_optimizer
pytest tests/expr_parser_test.py 
```

