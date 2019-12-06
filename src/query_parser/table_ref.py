class TableInfo:
    """
    stores all the table info, inspired from postgres
    """
    def __init__(self, table_name=None, schema_name=None, database_name=None):
        self._table_name = table_name
        self._schema_name = schema_name
        self._database_name = database_name

    @property
    def table_name(self):
        return self._table_name

    @property
    def schema_name(self):
        return self._schema_name

    @property
    def database_name(self):
        return self._database_name


class TableRef:
    """
    dummy class right now need to handle join expression
    Attributes:
    table_info: expression of table name and database name
    """
    def __init__(self, table_info: TableInfo):
        self._table_info = table_info

    @property
    def table_info(self):
        return self._table_info
