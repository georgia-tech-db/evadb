from typing import Generator, Iterator
import pandas as pd

from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.plan_nodes.project_plan import ProjectPlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager


class DeleteExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ProjectPlan):
        super().__init__(node)
        self.predicate = node.where_clause
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self, **kwargs) -> Iterator[Batch]:
        try:
            ########################################################
            ### Use the predicate to get the rows to be deleted ####
            ########################################################
            config_batch_mem_size = ConfigurationManager().get_value(
                "executor", "batch_mem_size"
            )
            batch_mem = 30000000
            if config_batch_mem_size:
                batch_mem = config_batch_mem_size
            table_catalog = self.node.table_ref.table.table_obj
            storage_engine = StorageEngine.factory(table_catalog)

            del_batch = Batch()

            if table_catalog.table_type == TableType.VIDEO_DATA:
                raise NotImplementedError("DELETE only implemented for structured data")
            elif table_catalog.table_type == TableType.IMAGE_DATA:
                raise NotImplementedError("DELETE only implemented for structured data")
            elif table_catalog.table_type == TableType.STRUCTURED_DATA:
                del_batch = storage_engine.read(table_catalog, batch_mem)
                del_batch = list(del_batch)[0]
            
            original_column_names = list(del_batch.frames.columns)
            column_names = [f"{table_catalog.name.lower()}.{name}" for name in original_column_names if not name=="_row_id"]
            column_names.insert(0, '_row_id')
            del_batch.frames.columns = column_names
            del_batch = apply_predicate(del_batch, self.predicate)

            ######################################################
            # All the batches that need to be deleted
            
            if table_catalog.table_type == TableType.VIDEO_DATA:
                storage_engine.delete(
                    table_catalog,
                    del_batch
                )
            elif table_catalog.table_type == TableType.IMAGE_DATA:
                storage_engine.delete(table_catalog, del_batch)
            elif table_catalog.table_type == TableType.STRUCTURED_DATA:
                del_batch.frames.columns = original_column_names
                table_needed = del_batch.frames[[f"{self.predicate.children[0].col_name}"]]
                # delete_dict = {
                #     self.predicate.children[0].col_name : table_needed.iloc[0]
                # }
                storage_engine.delete(table_catalog, table_needed.iloc[0])
            yield Batch(
            pd.DataFrame(
                [
                    f"Deleted row"
                ]
            )
            )
            
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(**kwargs)
