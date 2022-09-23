import pytest
import sys
from test.util import copy_sample_videos_to_upload_dir, file_remove, load_inbuilt_udfs

import mock
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

@pytest.fixture(scope='session')
def tearDownClass():
    yield None
    file_remove("ua_detrac.mp4")


@pytest.fixture(scope='session')
def setup_pytorch_tests():

    CatalogManager().reset()
    copy_sample_videos_to_upload_dir()
    query = """LOAD FILE 'ua_detrac.mp4'
                INTO MyVideo;"""
    execute_query_fetch_all(query)
    query = """LOAD FILE 'mnist.mp4'
                INTO MNIST;"""
    execute_query_fetch_all(query)
    load_inbuilt_udfs()



