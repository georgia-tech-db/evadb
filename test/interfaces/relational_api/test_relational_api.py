import os
import unittest
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR

from eva.interfaces.relational.db import connect
from eva.server.command_handler import execute_query_fetch_all
from test.util import load_udfs_for_testing, shutdown_ray
from pandas.testing import assert_frame_equal


class RelationalAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        os.system("nohup eva_server --port 8888 --start")
        CatalogManager().reset()
        self.mnist_path = f"{EVA_ROOT_DIR}/data/mnist/mnist.mp4"
        load_udfs_for_testing()

        self.images = f"{EVA_ROOT_DIR}/data/detoxify/*.jpg"

    def tearDown(self):
        shutdown_ray()
        # todo: move these to relational apis as well
        execute_query_fetch_all("""DROP TABLE IF EXISTS mnist_video;""")
        execute_query_fetch_all("""DROP TABLE IF EXISTS meme_images;""")
        os.system("nohup eva_server --stop")

    def test_relation_apis(self):
        conn = connect(port=8888)
        rel = conn.load(
            self.mnist_path,
            table_name="mnist_video",
            format="video",
        )
        rel.execute()

        rel = conn.table("mnist_video").select("_row_id, id")
        assert_frame_equal(
            rel.df(), conn.query("select _row_id, id from mnist_video;").df()
        )

        rel = rel.filter("id < 10")
        assert_frame_equal(
            rel.df(),
            conn.query("select _row_id, id from mnist_video where id < 10;").df(),
        )

        rel = rel.cross_apply(
            "unnest(MnistImageClassifier(data))", "mnist(label)"
        ).filter("mnist.label = 1")
        query = """ select _row_id, id
                    from mnist_video
                        join lateral unnest(MnistImageClassifier(data)) AS mnist(label) 
                    where id < 10 AND mnist.label = 1;"""
        print(rel.df())
        assert_frame_equal(rel.df(), conn.query(query).df())

        rel = conn.load(
            self.images,
            table_name="meme_images",
            format="image",
        )
        rel.execute()

        rel = conn.table("meme_images").select("_row_id, name")
        assert_frame_equal(
            rel.df(), conn.query("select _row_id, name from meme_images;").df()
        )

        rel = rel.filter("_row_id < 3")
        assert_frame_equal(
            rel.df(),
            conn.query("select _row_id, name from meme_images where _row_id < 3;").df(),
        )

    def test_relation_api_chaining(self):
        conn = connect(port=8888)
        rel = conn.load(
            self.mnist_path,
            table_name="mnist_video",
            format="video",
        )
        rel.execute()

        rel = (
            conn.table("mnist_video")
            .select("id, data")
            .filter("id > 10")
            .filter("id < 20")
        )
        assert_frame_equal(
            rel.df(),
            conn.query(
                "select id, data from mnist_video where id > 10 AND id < 20;"
            ).df(),
        )
