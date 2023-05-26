from typing import List
from eva.parser.load_statement import LoadDataStatement

from eva.parser.parser import Parser
from eva.parser.select_statement import SelectStatement
from eva.parser.table_ref import JoinNode


def parse_expression(expr: str):
    mock_query = f"SELECT {expr} FROM DUMMY;"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.target_list[0]


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


def parse_lateral_join(expr: str, alias: str):
    mock_query = f"SELECT * FROM DUMMY LATERAL JOIN {expr} AS {alias};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert isinstance(stmt.from_table, JoinNode)
    return stmt.from_table.join_node.right
