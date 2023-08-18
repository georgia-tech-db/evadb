# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import uuid
from pathlib import Path
from typing import Any, Dict, List

from evadb.catalog.catalog_type import (
    ColumnType,
    DocumentColumnName,
    ImageColumnName,
    NdArrayType,
    PDFColumnName,
    TableType,
    VideoColumnName,
)
from evadb.catalog.models.utils import (
    ColumnCatalogEntry,
    TableCatalogEntry,
    UdfCacheCatalogEntry,
    UdfCatalogEntry,
)
from evadb.catalog.sql_config import IDENTIFIER_COLUMN
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.executor.executor_utils import ExecutorError
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_statement import ColConstraintInfo, ColumnDefinition
from evadb.utils.generic_utils import get_str_hash, remove_directory_contents


def generate_sqlalchemy_conn_str(engine: str, params: Dict[str, str]):
    if engine == "postgres":
        conn_str = f"""postgresql://{params["user"]}:{params["password"]}@{params["host"]}:{params["port"]}/{params["database"]}"""
    else:
        raise ExecutorError(f"Native engine: {engine} is not currently supported")
    return conn_str


def is_video_table(table: TableCatalogEntry):
    return table.table_type == TableType.VIDEO_DATA


def is_document_table(table: TableCatalogEntry):
    return table.table_type == TableType.DOCUMENT_DATA


def is_pdf_table(table: TableCatalogEntry):
    return table.table_type == TableType.PDF_DATA


def is_string_col(col: ColumnCatalogEntry):
    return col.type == ColumnType.TEXT or col.array_type == NdArrayType.STR


def get_video_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: video path
    id: frame id
    data: frame data
    audio: frame audio
    """
    columns = [
        ColumnDefinition(
            VideoColumnName.name.name,
            ColumnType.TEXT,
            None,
            None,
            ColConstraintInfo(unique=True),
        ),
        ColumnDefinition(VideoColumnName.id.name, ColumnType.INTEGER, None, None),
        ColumnDefinition(
            VideoColumnName.data.name,
            ColumnType.NDARRAY,
            NdArrayType.UINT8,
            (None, None, None),
        ),
        ColumnDefinition(VideoColumnName.seconds.name, ColumnType.FLOAT, None, []),
    ]
    return columns


def get_image_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: image path
    data: image decoded data
    """
    columns = [
        ColumnDefinition(
            ImageColumnName.name.name,
            ColumnType.TEXT,
            None,
            None,
            ColConstraintInfo(unique=True),
        ),
        ColumnDefinition(
            ImageColumnName.data.name,
            ColumnType.NDARRAY,
            NdArrayType.UINT8,
            (None, None, None),
        ),
    ]
    return columns


def get_document_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: file path
    chunk_id: chunk id (0-indexed for each file)
    data: text data associated with the chunk
    """
    columns = [
        ColumnDefinition(
            DocumentColumnName.name.name,
            ColumnType.TEXT,
            None,
            None,
            ColConstraintInfo(unique=True),
        ),
        ColumnDefinition(
            DocumentColumnName.chunk_id.name, ColumnType.INTEGER, None, None
        ),
        ColumnDefinition(
            DocumentColumnName.data.name,
            ColumnType.TEXT,
            None,
            None,
        ),
    ]
    return columns


def get_pdf_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: pdf name
    page: page no
    paragraph: paragraph no
    data: pdf paragraph data
    """
    columns = [
        ColumnDefinition(PDFColumnName.name.name, ColumnType.TEXT, None, None),
        ColumnDefinition(PDFColumnName.page.name, ColumnType.INTEGER, None, None),
        ColumnDefinition(PDFColumnName.paragraph.name, ColumnType.INTEGER, None, None),
        ColumnDefinition(
            PDFColumnName.data.name,
            ColumnType.TEXT,
            None,
            None,
        ),
    ]
    return columns


def get_table_primary_columns(
    table_catalog_obj: TableCatalogEntry,
) -> List[ColumnDefinition]:
    """
    Get the primary columns for a table based on its table type.

    Args:
        table_catalog_obj (TableCatalogEntry): The table catalog object.

    Returns:
        List[ColumnDefinition]: The list of primary columns for the table.
    """
    primary_columns = [
        ColumnDefinition(IDENTIFIER_COLUMN, ColumnType.INTEGER, None, None)
    ]
    # _row_id for all the TableTypes, however for Video data and PDF data we also add frame_id (id) and paragraph as part of unique key
    if table_catalog_obj.table_type == TableType.VIDEO_DATA:
        # _row_id, id
        primary_columns.append(
            ColumnDefinition(VideoColumnName.id.name, ColumnType.INTEGER, None, None),
        )

    elif table_catalog_obj.table_type == TableType.PDF_DATA:
        # _row_id, paragraph
        primary_columns.append(
            ColumnDefinition(
                PDFColumnName.paragraph.name, ColumnType.INTEGER, None, None
            )
        )

    elif table_catalog_obj.table_type == TableType.DOCUMENT_DATA:
        # _row_id, chunk_id
        primary_columns.append(
            ColumnDefinition(
                DocumentColumnName.chunk_id.name, ColumnType.INTEGER, None, None
            )
        )

    return primary_columns


def xform_column_definitions_to_catalog_entries(
    col_list: List[ColumnDefinition],
) -> List[ColumnCatalogEntry]:
    """Create column catalog entries for the input parsed column list.

    Arguments:
        col_list {List[ColumnDefinition]} -- parsed col list to be created
    """

    result_list = []
    for col in col_list:
        column_entry = ColumnCatalogEntry(
            name=col.name,
            type=col.type,
            array_type=col.array_type,
            array_dimensions=col.dimension,
            is_nullable=col.cci.nullable,
        )
        # todo: change me
        result_list.append(column_entry)

    return result_list


def construct_udf_cache_catalog_entry(
    func_expr: FunctionExpression, cache_dir: str
) -> UdfCacheCatalogEntry:
    """Constructs a udf cache catalog entry from a given function expression.
    It is assumed that the function expression has already been bound using the binder.
    The catalog entry is populated with dependent udfs and columns by traversing the
    expression tree. The cache name is represented by the signature of the function
    expression.
    Args:
        func_expr (FunctionExpression): the function expression with which the cache is associated
        cache_dir (str): path to store the cache
    Returns:
        UdfCacheCatalogEntry: the udf cache catalog entry
    """
    udf_depends = []
    col_depends = []
    for expr in func_expr.find_all(FunctionExpression):
        udf_depends.append(expr.udf_obj.row_id)
    for expr in func_expr.find_all(TupleValueExpression):
        col_depends.append(expr.col_object.row_id)
    cache_name = func_expr.signature()

    # add salt to the cache_name so that we generate unique name
    path = str(get_str_hash(cache_name + uuid.uuid4().hex))
    cache_path = str(Path(cache_dir) / Path(f"{path}_{func_expr.name}"))
    args = tuple([arg.signature() for arg in func_expr.children])
    entry = UdfCacheCatalogEntry(
        name=func_expr.signature(),
        udf_id=func_expr.udf_obj.row_id,
        cache_path=cache_path,
        args=args,
        udf_depends=udf_depends,
        col_depends=col_depends,
    )

    return entry


def cleanup_storage(config):
    remove_directory_contents(config.get_value("storage", "index_dir"))
    remove_directory_contents(config.get_value("storage", "cache_dir"))
    remove_directory_contents(config.get_value("core", "datasets_dir"))


def get_metadata_entry_or_val(
    udf_obj: UdfCatalogEntry, key: str, default_val: Any = None
) -> str:
    """
    Return the metadata value for the given key, or the default value if the
    key is not found.

    Args:
        udf_obj (UdfCatalogEntry): An object of type `UdfCatalogEntry` which is
        used to extract metadata information.
        key (str): The metadata key for which the corresponding value needs to be retrieved.
        default_val (Any): The default value to be returned if the metadata key is not found.

    Returns:
        str: metadata value
    """
    for metadata in udf_obj.metadata:
        if metadata.key == key:
            return metadata.value
    return default_val


def get_metadata_properties(udf_obj: UdfCatalogEntry) -> Dict:
    """
    Return all the metadata properties as key value pair

    Args:
        udf_obj (UdfCatalogEntry): An object of type `UdfCatalogEntry` which is
        used to extract metadata information.
    Returns:
        Dict: key-value for each metadata entry
    """
    properties = {}
    for metadata in udf_obj.metadata:
        properties[metadata.key] = metadata.value
    return properties


#### get catalog instance
# This function plays a crucial role in ensuring that different threads do
# not share the same catalog object, as it can result in serialization issues and
# incorrect behavior with SQLAlchemy. Therefore, whenever a catalog instance is
# required, we create a new one. One possible optimization is to share the catalog
# instance across all objects within the same thread. It is worth investigating whether
# SQLAlchemy already handles this optimization for us, which will be explored at a
# later time.
def get_catalog_instance(db_uri: str, config: ConfigurationManager):
    from evadb.catalog.catalog_manager import CatalogManager

    return CatalogManager(db_uri, config)
