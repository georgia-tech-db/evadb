"""
Defines UADETRAC TableHandler.
Provides the methods to infer stats of a Table.
"""
import pandas as pd

from sqlite_connection import SqliteConnection
from base_table_handler import BaseTableHandler

class VideoFrameMap:
    def __init__(self, args):
        self.id = args['id']
        self.video_id = args['video_id']


class TableHandler(BaseTableHandler):
    def __init__(self, database_name, conn: SqliteConnection):
        BaseTableHandler.__init__(conn)
        self.table_name = database_name + "_mapping"
        self.conn = conn

    def __str__(self):
        return 'Frame(table_name=' + self.table_name + ',id=' + str(self.id) \
               + ',video_id=' + str(self.video_id) + ')'

    def create_table(self, conn):
        sql = """CREATE TABLE IF NOT EXISTS %s(id INTEGER 
                PRIMARY KEY,video_id INTEGER NOT NULL)""" % self.table_name
        conn.execute(sql)

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

    def drop_mapping(self, conn):
        sql = """drop table %s""" % self.table_name
        conn.execute(sql)


