import unittest


class RelationalAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_select(self):
        from eva.interfaces.relational_api.db_api import connect

        conn = connect()
        rel = conn.load(
            "./test/data/uadetrac/small-data/MVI_20011/*.jpg",
            table_name="detrac_images",
            format="image",
        )
        print(rel.execute())

        rel = conn.table("detrac_images")
        print(rel.execute())

        rel = rel.select(["_row_id", "name"])
        print(rel.execute())

        rel = rel.filter("_row_id < 3")
        print(rel.execute())
