from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager


class EVADB:
    def __init__(self, db_uri: str, config: ConfigurationManager) -> None:
        self._db_uri = db_uri
        self._config = config

        # intialize catalog manager
        self._catalog = CatalogManager(db_uri, config)

    @property
    def catalog(self):
        return self._catalog

    @property
    def config(self):
        return self._config
