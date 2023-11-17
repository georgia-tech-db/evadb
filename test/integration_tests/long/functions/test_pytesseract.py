import unittest

from test.util import get_evadb_for_testing

from evadb.server.command_handler import execute_query_fetch_all

class PytesseractTest(unittest.TestCase):

    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        
        load_image_query = """LOAD IMAGE 'data/ocr/Example.jpg' INTO MyImage;"""
        
        execute_query_fetch_all(self.evadb, load_image_query)

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyImage;")

    @unittest.skip("Needs Pytesseract")
    def test_pytesseract_function(self):
        function_name = "PyTesseractOCRFunction"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS{function_name}
            IMPL 'evadb/functions/pytesseract_function.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

        ocr_query = f"SELECT {function_name}(data) FROM MyImage;"
        output_batch = execute_query_fetch_all(self.evadb, ocr_query)
        self.assertEqual(1, len(output_batch))
        
    

