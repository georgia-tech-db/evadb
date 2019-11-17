"""
Defines UADETRAC TableHandler.
Provides the methods to infer stats of a Table.
"""
import pandas as pd

from src.catalog.sqlite_connection import SqliteConnection
from src import constants
from src.catalog.handlers.base_table_handler import BaseTableHandler

class VideoFrameMap:
    def __init__(self, args):
        self.id = args['id']
        self.video_id = args['video_id']


class UaDetracTableHandler(BaseTableHandler):
    """

    """

    def __init__(self, conn: SqliteConnection):
        self.dataset_name = constants.UADETRAC
        BaseTableHandler.__init__(conn)
        self.table_name = self.dataset_name + "_mapping"
        self.conn = conn

    def __str__(self):
        return 'Frame(table_name=' + self.table_name + ',id=' + str(self.id) \
               + ',video_id=' + str(self.video_id) + ')'

    def create_uadetrac_table(self, conn):
        sql = """CREATE TABLE IF NOT EXISTS %s(id INTEGER 
                PRIMARY KEY,video_id INTEGER NOT NULL)""" % self.table_name
        self.create_table(sql)

    def add_frame_mapping(self, conn, video_start_indices, num_frames):
        insert_script = """"""
        video_id = 0
        for i in range(num_frames):
            if video_id + 1 < len(video_start_indices) and i == \
                    video_start_indices[video_id + 1]:
                video_id += 1
            sql = """insert into %s(id, video_id) values(%s, %s);""" % (
                self.table_name, i, video_id)
            insert_script += sql
        conn.exec_multiple(insert_script)

    def get_frame_ids(self, conn, video_id):
        sql = """select * from %s  where video_id = %s""" % (
            self.table_name, video_id)
        df = pd.read_sql_query(sql, conn.conn)
        mappings = [VideoFrameMap(args) for args in df.to_dict(
            orient='records')]
        return [m.id for m in mappings]


