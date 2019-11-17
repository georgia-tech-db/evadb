"""
Catalog is single entry to access Eva Catalog.

Usage:
#TODO(rishabh): Add usage examples here.
"""

import os
import logging

from src.catalog.sqlite_connection import SqliteConnection
from src.catalog.handlers.prob_predicate_handler import ProbPredicateHandler
from src.catalog.handlers.base_table_handler import BaseTableHandler
from src.catalog.handlers.uadetrac_table_handler import UaDetracTableHandler
from src import constants


class Catalog:
    """
        Catalog provides all the meta information for a database. Its methods can be used
        to add, refresh and query the existing meta information.
        Table meta can be queried using TableHandler and Probabilistic Filter meta information can be
        queried with ProbPredicateHandler.
    """

    def __init__(self, dataset_name: str = None):
        self.current_dataset = dataset_name
        # TODO(rishabh): Read the logger level from config file.
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.db_file_map = {constants.UADETRAC: 'eva.db'}
        self.db_file_name = 'eva.db'
        self.conn = self._createDatabaseConnection()


    def listDatasets(self) -> list():
        """
        Return all existing supported datasets in Eva.
        :return: list[str]: A list containing databases names.
        """
        return list(self.db_file_map.keys())

    def setDataset(self, dataset: str) -> None:
        """
        Set the current dataset.
        :param database: str, Name of the dataset.
        """
        self.current_dataset = dataset

    def getCurrentDataset(self) -> str:
        """
        Return the name of the current database to be used.
        :return: str, database name.
        """
        self._checkDatabaseSet()
        return self.current_dataset

    def getTableHandler(self) -> BaseTableHandler:
        """
        TODO(rishabh): Add detailed definition and examples after finalizing TableHandler methods.

        :return:
        """
        self._checkDatabaseSet()
        if self.current_dataset == constants.UADETRAC:
            table_handler = UaDetracTableHandler(self.conn)
            return table_handler
        else:
            raise Exception('No implementation found for %s' % (self.current_dataset))

    def getProbPredicateHandler(self) -> ProbPredicateHandler:
        """
        TODO(rishabh): Add detailed definition and examples after finalizing PPHandler methods.
        :return:
        """
        self._checkDatabaseSet()
        pp_handler = ProbPredicateHandler(self.current_dataset, self.conn)
        return pp_handler

    def _checkDatabaseSet(self) -> None:
        " Checks if a catalog is initialised with a dataset."

        if not self.current_dataset:
            raise Exception('Dataset is not set.')

    def _createDatabaseConnection(self) -> SqliteConnection:
        eva_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        cache_dir = os.path.join(eva_dir, 'cache')
        catalog_dir = os.path.join(eva_dir, 'src', 'catalog')
        try:
            conn = SqliteConnection(os.path.join(catalog_dir, self.db_file_map[self.current_dataset]))
        except:
            raise Exception('Database file not found')
        conn.connect()
        return conn

    def getDatabaseConnection(self) -> SqliteConnection:
        """
           TODO(rishabh): This needs to be deleted. Used to support existing code. Discuss this.
        :return:
        """
        return self.conn



