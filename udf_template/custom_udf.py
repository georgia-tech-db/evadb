from udf_template.udf_template import UDFTemplate


class CustomUDF(UDFTemplate):
    def __init__(self, query):
        self.udf_query = query

    def process(self, data_df):
        new_df = None
        # custom filter code for this UDF
        return new_df
