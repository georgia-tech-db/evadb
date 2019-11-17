"""

"""
from abc import ABCMeta

from sqlite_connection import SqliteConnection


class BaseTableHandler(metaclass=ABCMeta):

     def __init__(self, conn: SqliteConnection):
         self.conn = conn

     def create_table(self, sql) -> None:
         """

         :param sql:
         :return:
         """
         self.conn.execute(sql)

     def drop_table(self, table_name) -> None:
         sql = """drop table %s""" % table_name
         self.conn.execute(sql)
