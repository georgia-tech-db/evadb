import datetime
import numpy as np
import pandas as pd
import time

from eva.udfs.abstract_udf import AbstractUDF


class Timestamp(AbstractUDF):
    @property
    def name(self) -> str:
        return "Timestamp"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        inp: DataFrame
            col1        
        0   int    
        1   int    
        out: DataFrame
            timestamp
        0   string
        1   string
        """
        # sanity check
        if len(inp.columns) != 1:
            raise ValueError("input contains wrong number of columns")

        seconds = pd.DataFrame(inp[inp.columns[0]])
        timestamp_result = seconds.apply(
            lambda x: self.format_timestamp(x[0]), axis=1
        )
        return pd.DataFrame({"timestamp": timestamp_result.values})

    def format_timestamp(self, num_of_seconds):
        timestamp = time.strftime('%H:%M:%S', time.gmtime(num_of_seconds))
        return timestamp