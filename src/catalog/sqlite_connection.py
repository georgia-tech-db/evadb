import os
import sqlite3
import sys
import time
from importlib import import_module
from src.catalog.catalog import Catalog

try:
    from src.catalog.entity.dataset import Dataset
except ImportError:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
        __file__))))
    # print(root)
    sys.path.append(root)
    from src.catalog.entity.dataset import Dataset
from src.catalog.mapping_manager import MappingManager
from src.editing_opr.apply_opr import Operator
from src.storage.loader_uadetrac import LoaderUadetrac


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


def get_loader(cache_dir, name, loaded_height, loaded_width):
    mod_name = 'src.storage.' + 'loader_' + name
    mod = import_module(mod_name)
    loader_class = getattr(mod, 'Loader' + name.capitalize())
    return loader_class(loaded_width, loaded_height, cache_dir)


if __name__ == "__main__":
    UADETRAC = 'uadetrac'
    eva_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    cache_dir = os.path.join(eva_dir, 'cache')
    catalog_dir = os.path.join(eva_dir, 'src', 'catalog')

    # conn = SqliteConnection(os.path.join(catalog_dir, 'eva.db'))
    # conn.connect()
    catalog = Catalog(UADETRAC)
    # conn.exec_script(os.path.join(catalog_dir, 'scripts',
    # 'create_table.sql'))

    # conn.exec_script(os.path.join(catalog_dir, 'scripts',
    # 'create_table.sql'))

    # create dataset
    conn = catalog.getDatabaseConnection()
    Dataset.delete_all(conn.conn, UADETRAC)
    loaded_width = loaded_height = 300
    Dataset.create(conn.conn, UADETRAC, 540, 960, loaded_height, loaded_width)
    #
    # # use dataset
    dataset = Dataset.get(conn, UADETRAC)
    print(dataset)
    #
    # # get loader for dataset
    loader = LoaderUadetrac(loaded_width, loaded_height, cache_dir)

    # load video/frames
    data_dir = os.path.join(eva_dir, 'data', 'ua_detrac',
                            'Insight-MVT_Annotation_Test')

    video_dir_list = os.listdir(data_dir)
    video_dir_list.sort()
    for video_dir in video_dir_list[:5]:
        loader.load_images(os.path.join(data_dir, video_dir))
    print("Number of images loaded: %s" % len(loader.images))

    # print(loader.images.shape)
    loader.save_images()
    mmanager = catalog.getTableHandler()
    # mmanager = MappingManager(UADETRAC)
    mmanager.drop_mapping(conn)
    mmanager.create_table(conn)
    mmanager.add_frame_mapping(conn, loader.video_start_indices,
                               loader.images.shape[0])

    frame_ids = mmanager.get_frame_ids(conn, 3)
    images_arr = loader.get_frames(frame_ids)
    images_list = list(images_arr)
    print(len(images_list))

    operator = Operator()
    s = time.time()
    images_list = operator.transform(['grayscale'], images_list)
    loader.update_images(frame_ids, images_list, False)
    e = time.time()
    print((e - s)/len(images_list))

    s = time.time()
    images_list = operator.transform(['grayscale', 'blur'], images_list,
                                     {"kernel_size": 5})
    loader.update_images(frame_ids, images_list, False)
    e = time.time()
    print((e - s)/len(images_list))
