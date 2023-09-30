from evadb.catalog.catalog_type import VideoColumnName
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.binder.statement_binder import StatementBinder


def bind_tuple_expr(binder: StatementBinder, node: TupleValueExpression):
    table_alias, col_obj = binder._binder_context.get_binded_column(
        node.name, node.table_alias
    )
    node.table_alias = table_alias
    if node.name == VideoColumnName.audio:
        binder._binder_context.enable_audio_retrieval()
    if node.name == VideoColumnName.data:
        binder._binder_context.enable_video_retrieval()
    node.col_alias = "{}.{}".format(table_alias, node.name.lower())
    node.col_object = col_obj