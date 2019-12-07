"""
Implement methods to add, get, update, delete a probabilistic predicate.
Usage:
 TODO(rishabh): Add examples.
"""
import logging

from src.catalog.sqlite_connection import SqliteConnection


class ProbPredicateHandler:
    def __init__(self, database_name: str, conn: SqliteConnection):
        self.pp_dataset_name = database_name
        self.conn = conn
        self.pp_table_name = "pp_filter"

    def addProbabilisticFilter(
            self,
            name: str,
            reduction_rate: float,
            filter_cost: float,
            accuracy: float,
            udf_cost: float,
            model_type: str,
    ) -> None:
        """

        :param name:
        :param reduction_rate:
        :param filterCost:
        :param accuracy:
        :param udf_cost:
        :param model_type:
        :return:
        """
        sql = """insert into %s(name, reduction_rate, filter_cost, accuracy,
         udf_cost, dataset_name, model_type)
                 values('%s', %s, %s, %s, '%s', '%s', '%s')""" % (
            self.pp_table_name,
            name,
            reduction_rate,
            filter_cost,
            accuracy,
            udf_cost,
            self.pp_dataset_name,
            model_type,
        )
        self.conn.execute(sql)

    def updateProbabilisticFilter(
            self,
            name: str,
            reduction_rate: float,
            filterCost: float,
            accuracy: float,
            udf_cost: float,
            model_type: str,
    ) -> None:
        """

        :param name:
        :param reduction_rate:
        :param filterCost:
        :param accuracy:
        :param udf_cost:
        :param model_type:
        :return:
        """
        pass

    def listProbilisticFilters(self) -> list():
        """
        List all probabilistic filter names which
        exists for the current dataset.
        :return: lits[str], name of filter names
        """
        sql = """select distinct(name) from pp_filter 
        where dataset_name = '%s'""" % (
            self.pp_dataset_name
        )
        logging.info("Fetching all filters with " + sql)
        filters_list = self.conn.execute_and_fetch(sql)
        return filters_list

    def getProbabilisticFilter(self, name: str) -> list():
        """

        :param name:
        :return:
        """
        sql = """select * from pp_filter
         where name='%s' and dataset_name = '%s'""" % (
            name,
            self.pp_dataset_name,
        )
        logging.info("Fetching filter info for " + name + " using " + sql)
        filter_info = self.conn.execute_and_fetch(sql)
        # TODO(rishabh): Check if we should return a PPFilter Object. Needs to
        # be defined.
        return filter_info

    def deleteProbilisticFilter(self, name: str) -> None:
        pass
