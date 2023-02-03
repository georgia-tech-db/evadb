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
import os
import unittest
from test.util import create_dummy_batches, create_sample_video, file_remove

import boto3
import pandas as pd
from moto import mock_s3

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from eva.server.command_handler import execute_query_fetch_all


class S3LoadExecutorTest(unittest.TestCase):
    mock_s3 = mock_s3()
    bucket_name = "test-bucket"

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        self.video_file_path = create_sample_video()
        self.s3_download_dir = ConfigurationManager().get_value(
            "storage", "s3_download_dir"
        )

        """Mocked AWS Credentials for moto."""
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

        self.mock_s3.start()

        # you can use boto3.client("s3") if you prefer
        s3_resource = boto3.resource("s3")
        bucket = s3_resource.Bucket(self.bucket_name)
        bucket.create()

    def tearDown(self):
        file_remove("MyVideo/dummy.avi", parent_dir=self.s3_download_dir)
        self.mock_s3.stop()

    def test_s3_single_file_load_executor(self):
        s3_client = boto3.client("s3")
        s3_client.upload_file(self.video_file_path, self.bucket_name, "dummy.avi")

        query = f"LOAD VIDEO 's3://{self.bucket_name}/dummy.avi' INTO MyVideo;"
        execute_query_fetch_all(query)

        select_query = """SELECT * FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(video_dir=f"{self.s3_download_dir}/MyVideo")
        )[0]
        self.assertEqual(actual_batch, expected_batch)
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_s3_multiple_file_load_executor(self):
        s3_client = boto3.client("s3")

        video_path = f"{EVA_ROOT_DIR}/data/sample_videos/1"

        for file in os.listdir(video_path):
            s3_client.upload_file(f"{video_path}/{file}", self.bucket_name, file)

        query = f"""LOAD VIDEO "s3://{self.bucket_name}/*.mp4" INTO MyVideos;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 2"])
        )
        self.assertEqual(result, expected)

        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideos;")
