

import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from statsforecast.adapters.prophet import AutoARIMAProphet

class MultivariateForecast(AbstractFunction):
    @property
    def name(self) -> str:
        return "MultivariateForecast"


    @setup(cacheable=False, function_type="Forecasting", batchable=True)
    def setup(self, train_end_date=None):
        self.train_end_date = train_end_date
        
    
    @forward(
        input_signatures=[],
        output_signatures=[
            PandasDataframe(
                columns=["ds", "y"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,), (None,)],
            )
        ],
    )
    def forward(self, data) -> pd.DataFrame:
        
        train_df = data[data['ds']<=self.train_end_date]
        test_df = data[data['ds']>self.train_end_date]
        
        #instantiate the model
        auto_arima_prophet = AutoARIMAProphet()
        auto_arima_prophet.fit(train_df)
        
        try:
            test_inp = test_df.drop(['y'], axis=1)
        except:
            pass
        
        predictions = auto_arima_prophet.predict(test_df)
        final_preds = predictions[['ds', 'yhat']]
        final_preds = final_preds.rename(columns={'yhat':'y'})
        
        return final_preds
        
        
        
        
        