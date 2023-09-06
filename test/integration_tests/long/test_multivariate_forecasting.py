import unittest
from test.markers import forecast_skip_marker
from test.util import get_evadb_for_testing, shutdown_ray

import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all

@pytest.mark.notparallel
class MultivariateFcstModelTrainTests(unittest.TestCase):

    def setUp(self):
        self.evadb = get_evadb_for_testing()
        
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

        
    
    @forecast_skip_marker
    def test_forecast(self):
        
        drop_table_query = """
        DROP TABLE IF EXISTS AirQualityData;
        """
        
        execute_query_fetch_all(self.evadb, drop_table_query)
        
        
        create_table_query = """
            CREATE TABLE AirQualityData (
            unique_id INTEGER,
            ds TEXT(40),
            co_gt FLOAT(64,64),
            pt_08_s1_co FLOAT(64,64),
            nmhc_gt FLOAT(64,64),
            c6h6_gt FLOAT(64,64),
            pt08_s2_nmhc FLOAT(64,64),
            nox_gt FLOAT(64,64),
            pt08_s3_nox FLOAT(64,64),
            no2_gt FLOAT(64,64),
            pt08_s4_no2 FLOAT(64,64),
            pt08_s5_o3 FLOAT(64,64),
            rh FLOAT(64,64),
            ah FLOAT(64,64),
            y FLOAT(64,64)
            );"""
        
        execute_query_fetch_all(self.evadb, create_table_query)

        path = f"{EvaDB_ROOT_DIR}/data/forecasting/air_quality.csv"
        load_query = f"LOAD CSV '{path}' INTO AirQualityData;"
        execute_query_fetch_all(self.evadb, load_query)
        
        
        create_predict_udf = """
           CREATE FUNCTION MultivariateForecast IMPL 'evadb/functions/multivariate_forecast.py'
           train_end_date '2005-02-07';
        """
        
        execute_query_fetch_all(self.evadb, create_predict_udf)

        predict_query = """
            SELECT MultivariateForecast(*) FROM AirQualityData;
        """
        
        result = execute_query_fetch_all(self.evadb, predict_query)
        print(result)
        
        # unique_id, ds, 
        #     CO_GT, PT08_S1_CO, NMHC_GT,
        #     C6H6_GT, PT08_S2_NMHC, NOx_GT,
        #     PT08_S3_NOx, NO2_GT, PT08_S4_NO2,
        #     PT08_S5_O3, RH, AH,
        #     y 
    
    def tearDown(self):
        shutdown_ray()

        # clean up
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS AirQualityData;")
        
if __name__ == "__main__":
    suite = unittest.TestSuite()
    my_test = MultivariateFcstModelTrainTests()
    suite.addTest(MultivariateFcstModelTrainTests("test_forecast"))
    unittest.TextTestRunner().run(suite)
