from src.catalog.catalog_manager import CatalogManager
from src.planner.drop_plan import DropPlan
from src.executor.abstract_executor import AbstractExecutor
from src.storage.storage_engine import StorageEngine


class DropExecutor(AbstractExecutor):

    def __init__(self, node: DropPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """ Drop table executor """

        tables_to_drop = self.node.table_refs
        tables_to_drop_ids = self.node.table_ids
        if_exists = self.node.if_exists

        for table_id in tables_to_drop_ids:
            CatalogManager()._dataset_service.delete_dataset_by_id(table_id)
