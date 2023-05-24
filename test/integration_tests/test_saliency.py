# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from test.util import (
    NUM_FRAMES,
    create_sample_video,
    file_remove,
    load_udfs_for_testing,
    shutdown_ray,
)

import pandas as pd
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all

# import matplotlib.pyplot as plt
# import matplotlib as mpl
# # mpl.use('TkAgg')
# plt.ioff()


@pytest.mark.notparallel
class SaliencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        # video_file_path = create_sample_video(NUM_FRAMES)

        # Saliency1 = f"/Users/afaanansari/Desktop/gtech/eva_pdf_load/eva/test/integration_tests/test1.jpeg"
        # Saliency2 = f"/Users/afaanansari/Desktop/gtech/eva_pdf_load/eva/test/integration_tests/test2.jpeg"


        # load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        # execute_query_fetch_all(f"LOAD IMAGE '{Saliency1}' INTO MRI;")
        # execute_query_fetch_all(f"LOAD IMAGE '{Saliency2}' INTO MRI;")
        # execute_query_fetch_all(load_query)
        # load_udfs_for_testing(mode="minimal")

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        # execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all("DROP TABLE IF EXISTS SALIENCY;")
        # file_remove("dummy.avi")

    # integration test

    # def test_load_image(self):
    #     Saliency1 = f"data/saliency/test1.jpeg"
    #     create_udf_query = f"LOAD IMAGE '{Saliency1}' INTO SALIENCY;"
       
    #     execute_query_fetch_all(create_udf_query)

    def test_saliency(self):
        Saliency1 = f"data/saliency/test1.jpeg"
        create_udf_query = f"LOAD IMAGE '{Saliency1}' INTO SALIENCY;"
       
        execute_query_fetch_all(create_udf_query)
        create_udf_query = """CREATE UDF IF NOT EXISTS SaliencyMaps
                  INPUT (data NDARRAY UINT8(3, 224, 224)) 
                  OUTPUT (saliency ANYTYPE) 
                  TYPE  Classification 
                  IMPL 'eva/udfs/saliency_map.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query_saliency = """SELECT data, SaliencyMaps(data)
                        FROM SALIENCY;
                       """
        actual_batch_saliency = execute_query_fetch_all(select_query_saliency)
        print(actual_batch_saliency.frames)
        
        # df = actual_batch_saliency.frames
        # fig, ax = plt.subplots(nrows=2, ncols=len(df), figsize=[15,18])

        # for i in range(len(df)):
        #     img = df['mri.data'].iloc[i]
        #     ax[0,i].imshow(img)
        #     ax[1,i].imshow(df["mricnn.saliency"][i][0],cmap=plt.cm.hot)
        #     ax[0,i].axis('off')
        #     ax[1,i].axis('off')
        # plt.gcf().set_size_inches(5, 5)
        # plt.show()