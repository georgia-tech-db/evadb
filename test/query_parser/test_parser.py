import unittest
from src.query_parser.eva_parser import EvaFrameQLParser

class ParserTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_basic_visitor(self):
        eva = EvaFrameQLParser()
        query = "SELECT CLASS , REDNESS FROM TAIPAI WHERE CLASS = 'VAN' AND REDNESS = 3  OR REDNESS > 300.23; GROUP BY CLASS HAVING REDNESS > 20 ORDER BY REDNESS;"
        eva.build_eva_parse_tree(query)

if __name__ == '__main__':
    unittest.main()
