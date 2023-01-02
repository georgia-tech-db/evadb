from sqlalchemy import Column, ForeignKey, Table
from base_model import BaseModel

# dependency table to maintain a many-to-many relationship between udf_catalog and udf_cache_catalog. This is important to ensure that any changes to udf are propogated to udf_cache. For example, deletion of a udf should also clear the associated caches.

depend_udf_and_udf_cache = Table(
    "depend_udf_and_udf_cache",
    BaseModel.metadata,
    Column("_udf_id", ForeignKey("udf_catalog.id")),
    Column("_udf_cache_id", ForeignKey("udf_cache.id")),
)


depend_column_and_udf_cache = Table(
    "depend_column_and_udf_cache",
    BaseModel.metadata,
    Column("_col_id", ForeignKey("column_catalog.id")),
    Column("_udf_cache_id", ForeignKey("udf_cache.id")),
)
