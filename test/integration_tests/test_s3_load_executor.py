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
from moto import mock_s3
import os
import boto3

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from test.util import (
    create_dummy_batches_s3,
    create_sample_video,
    file_remove_from_s3,
)


class S3LoadExecutorTest(unittest.TestCase):
    mock_s3 = mock_s3()
    bucket_name = "test-bucket"

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        self.video_file_path = create_sample_video()

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

        s3_client = boto3.client('s3')
        s3_client.upload_file(self.video_file_path, self.bucket_name, "dummy.avi")


    def tearDown(self):
        file_remove_from_s3("MyVideo/dummy.avi")
        self.mock_s3.stop()


    def test_s3_load_executor(self):
        query = f"LOAD VIDEO 's3://{self.bucket_name}/dummy.avi' INTO MyVideo;"
        execute_query_fetch_all(query)

        select_query = """SELECT * FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches_s3())[0]
        self.assertEqual(actual_batch, expected_batch)
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
