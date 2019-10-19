import os
import sqlite3
from importlib import import_module

from src.catalog.entity.dataset import Dataset
from src.editing_opr.apply_opr import ApplyOpr
import cv2

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

    def execute(self, sql):
        query = '''%s''' % sql
        self.cursor.execute(query)
        self.conn.commit()


def get_loader(cache_dir, name, loaded_height, loaded_width):
    mod_name = 'src.storage.' + 'loader_' + name
    mod = import_module(mod_name)
    loader_class = getattr(mod, 'Loader' + name.capitalize())
    return loader_class(loaded_width, loaded_height, cache_dir)


if __name__ == "__main__":
    eva_src_dir = os.path.dirname(os.getcwd())
    eva_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    db_file = os.path.join(eva_src_dir, 'catalog', "eva.db")
    conn = SqliteConnection(db_file)
    conn.connect()
    # conn.exec_script(os.path.join(eva_src_dir, 'catalog', 'scripts',
    #                               'create_table.sql'))

    # create dataset
    UADETRAC = 'uadetrac'
    Dataset.delete_all(conn.conn, UADETRAC)
    Dataset.create(conn.conn, UADETRAC, 540, 960, 300, 300)

    # use dataset
    dataset = Dataset.get(conn.conn, UADETRAC)

    # get loader for dataset
    loader = get_loader(os.path.join(eva_dir, 'cache'), dataset.name,
                        dataset.loaded_height, dataset.loaded_width)

    # load video/frames
    data_dir = os.path.join(eva_dir, 'test', 'data', 'small-data')

    video_dir_list = os.listdir(data_dir)
    video_dir_list.sort()
    for video_dir in video_dir_list:
        loader.load_images(os.path.join(data_dir, video_dir), conn)

    # apply grayscale
    ApplyOpr.apply(loader, 1)
    edited_imgs = loader.load_cached_images(1)
    print(edited_imgs.shape[0])
    for i in range(edited_imgs.shape[0]):
        cv2.imwrite(os.path.join(eva_dir, str(i) + '.png'), edited_imgs[i])
