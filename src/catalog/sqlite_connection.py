import os
import sqlite3
from src.catalog.entity.dataset import Dataset


class SqliteConnection:

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def exec_script(self, script):
        f = open(script, "r")
        sql = f.read()
        sql = '''%s''' % sql
        self.cursor.executescript(sql)
        self.conn.commit()

    def insert(self, sql):
        query = '''%s''' % sql
        self.cursor.execute(query)
        self.conn.commit()


if __name__ == "__main__":
    eva_src_dir = os.path.dirname(os.getcwd())
    # print(eva_src_dir)
    db_file = os.path.join(eva_src_dir, 'catalog', "eva.db")
    conn = SqliteConnection(db_file)
    conn.connect()
    conn.exec_script(os.path.join(eva_src_dir, 'catalog', 'scripts',
                                  'create_table.sql'))
    # Dataset.create(conn, 'uadetrac', 540, 960, 300, 300)
    dataset = Dataset.get('uadetrac', conn.conn)
    print(dataset)


