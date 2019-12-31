import unittest

from pyspark.sql import SparkSession

from src.spark.session import Session


class SparkSessionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_session(self):

        application_name = "default"
        session = Session(application_name)

        spark_session = session.get_session()

        self.assertIsInstance(spark_session, SparkSession)


if __name__ == '__main__':

    unittest.main()
