"""
Catalog is single entry to access Eva Catalog.

Usage:
#TODO(rishabh): Add usage examples here.
"""

import os
import logging

from sqlite_connection import SqliteConnection
from handlers.table_handler import TableHandler
from handlers.prob_predicate_handler import ProbPredicateHandler
from src import constants


class Catalog:
    """
        Catalog provides all the meta information for a database. Its methods can be used
        to add, refresh and query the existing meta information.
        Table meta can be queried using TableHandler and Probabilistic Filter meta information can be
        queried with ProbPredicateHandler.
    """

    def __init__(self, database_name: str = None):
        self.current_database = database_name
        # TODO(rishabh): Read the logger level from config file.
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.db_file_map = {constants.UADETRAC: 'eva.db'}
        self.conn = self._createDatabaseConnection()


    def listDatabases(self) -> list[str]:
        """
        Return all existing database names.
        :return: list[str]: A list containing databases names.
        """
        return list(self.db_file_map.keys())

    def setDatabase(self, database: str) -> None:
        """
        Set the current database.
        :param database: str, Name of the database.
        """
        self.logger.info('Changing current database from %s to %s', self.current_database, database)
        self.conn = self._createDatabaseConnection()
        self.current_database = database

    def getCurrentDatabase(self) -> str:
        """
        Return the name of the current database to be used.
        :return: str, database name.
        """
        self._checkDatabaseSet()
        return self.current_database

    def getTableHandler(self) -> TableHandler:
        """
        TODO(rishabh): Add detailed definition and examples after finalizing TableHandler methods.

        :return:
        """
        self._checkDatabaseSet()
        table_handler = TableHandler(self.current_database, self.conn)
        return table_handler

    def getProbPredicateHandler(self) -> ProbPredicateHandler:
        """
        TODO(rishabh): Add detailed definition and examples after finalizing PPHandler methods.
        :return:
        """
        self._checkDatabaseSet()
        pp_handler = ProbPredicateHandler(self.current_database, self.conn)
        return pp_handler

    def _checkDatabaseSet(self) -> None:
        " Checks if a database if a catalog is initialised with a database."

        if not self.current_database:
            raise Exception('Database is not set.')

    def _createDatabaseConnection(self) -> SqliteConnection:
        eva_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        cache_dir = os.path.join(eva_dir, 'cache')
        catalog_dir = os.path.join(eva_dir, 'src', 'catalog')
        try:
            conn = SqliteConnection(os.path.join(catalog_dir, self.db_file_map[self.current_database]))
        except:
            raise Exception('Database file not found for %s', self.current_database)
        conn.connect()
        return conn

    def getDatabaseConnection(self) -> SqliteConnection:
        """
           TODO(rishabh): This needs to be deleted. Used to support existing code. Discuss this.
        :return:
        """
        return self.conn



