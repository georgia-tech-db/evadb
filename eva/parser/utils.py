from eva.parser.load_statement import LoadDataStatement

from eva.parser.parser import Parser
from eva.parser.select_statement import SelectStatement


def parse_expression(expr: str):
    mock_query = f"SELECT {expr} FROM DUMMY;"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.target_list


def parse_predicate_expression(expr: str):
    mock_query = f"SELECT * FROM DUMMY WHERE {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.where_clause


def parse_table_clause(expr: str):
    mock_query = f"SELECT * FROM {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_table_atom
    return stmt.from_table


def parse_load(table_name: str, file_regex: str, format: str, **kwargs):
    mock_query = f"LOAD {format.upper()} '{file_regex}' INTO {table_name};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, LoadDataStatement), "Expected a load statement"
    return stmt


def parse_query(query):
    stmt = Parser().parse(query)
    assert len(stmt) == 1
    return stmt[0]


def parse_lateral_join(expr: str, alias: str):
    mock_query = f"SELECT * FROM DUMMY JOIN LATERAL {expr} AS {alias};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_join()
    return stmt.from_table.join_node.right


def parse_create_vector_index(index_name: str, table_name: str, expr: str, using: str):
    mock_query = f"CREATE INDEX {index_name} ON {table_name} ({expr}) USING {using};"
    stmt = Parser().parse(mock_query)[0]
    return stmt


def parse_sql_orderby_expr(expr: str):
    mock_query = f"SELECT * FROM DUMMY ORDER BY {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.orderby_list
