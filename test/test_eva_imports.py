import os
import shutil
import unittest


class EVAImportTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_eva_cli_imports(self):
        """
        Testing imports for running client and server packages,
        when current working directory is changed.
        """
        cur_dir = os.getcwd()
        new_dir = os.path.join('test_eva', 'test')
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        os.chdir(new_dir)
        from eva import eva_cmd_client  # noqa: F401
        from eva import eva_server  # noqa: F401
        os.chdir(cur_dir)
        shutil.rmtree(new_dir)
