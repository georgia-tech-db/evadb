from udf_template.udf_template import UDFTemplate


class ReducerUDF(UDFTemplate):
    def __init__(self, query):
        self.udf_query = query

    def process(self, data_df):
        new_df = None
        # Reducer code for this UDF
        return new_df
