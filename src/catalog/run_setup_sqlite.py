import json
import sqlite3
import sys

from src.catalog.catalog import *

try:
    from src.catalog.entity.dataset import Dataset
except ImportError:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
        __file__))))
    sys.path.append(root)
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

    def exec_multiple(self, concatenated_sql):
        self.cursor.executescript(concatenated_sql)
        self.conn.commit()

    def execute(self, sql):
        query = '''%s''' % sql
        self.cursor.execute(query)
        self.conn.commit()

    def execute_and_fetch(self, sql):
        sql = '''%s''' % sql
        self.cursor.execute(sql)
        return self.cursor.fetchall()


if __name__ == "__main__":
    UADETRAC = 'uadetrac'
    eva_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    cache_dir = os.path.join(eva_dir, 'cache')
    catalog_dir = os.path.join(eva_dir, 'src', 'catalog')

    with open('../../query_optimizer/utils/synthetic_pp_stats.json') as f2:
        synthetic_pp_stats = json.load(f2)
    print(synthetic_pp_stats)
    conn = SqliteConnection(os.path.join(catalog_dir, 'pps.db'))
    conn.connect()
    # catalog = Catalog(UADETRAC)
    conn.exec_script(os.path.join(catalog_dir, 'scripts',
                                  'create_pp_filter.sql'))

    for key in synthetic_pp_stats:
        for model in synthetic_pp_stats[key]:
            sql = """insert into %s (
            name, 
            reduction_rate, 
            filter_cost, 
            accuracy, 
            udf_cost, 
            dataset_name, 
            model_type) 
                         values('%s', %s, %s, %s, '%s', '%s', '%s')""" % (
                "pp_filter",
                key,
                synthetic_pp_stats[key][model]['R'],
                synthetic_pp_stats[key][model]['C'],
                synthetic_pp_stats[key][model]['A'],
                "0",
                "UADETRAC",
                model
            )
            conn.execute(sql)
    conn.close()
