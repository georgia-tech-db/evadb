from udf_template.custom_udf import CustomUDF

def process(udf_object, data_df):

    if isinstance(udf_object, CustomUDF):
        # process data_df with customUDF's process function or any custom logic which is local to this specific UDF.
        return udf_object.process(data_df)