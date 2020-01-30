from sqlalchemy import Column, String, Integer


class DataFrameMetadata(object):
    __tablename__ = 'df_metadata'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String)
    _file_url = Column('file_url', String)
    _schema_id = Column('schema_id', Integer)

    def __init__(self,
                 dataframe_file_url,
                 dataframe_schema
                 ):
        self._file_url = dataframe_file_url
        self._dataframe_schema = dataframe_schema
        self._dataframe_petastorm_schema = \
            dataframe_schema.get_petastorm_schema()
        self._dataframe_pyspark_schema = \
            self._dataframe_petastorm_schema.as_spark_schema()

    def set_schema(self, schema):
        self._dataframe_schema = schema
        self._dataframe_petastorm_schema = \
            schema.get_petastorm_schema()
        self._dataframe_pyspark_schema = \
            self._dataframe_petastorm_schema.as_spark_schema()

    def get_id(self):
        return self._id

    def get_dataframe_file_url(self):
        return self._file_url

    def get_schema_id(self):
        return self._schema_id

    def get_dataframe_schema(self):
        return self._dataframe_schema

    def get_dataframe_petastorm_schema(self):
        return self._dataframe_petastorm_schema

    def get_dataframe_pyspark_schema(self):
        return self._dataframe_pyspark_schema
