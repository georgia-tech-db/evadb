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

from pathlib import Path

import boto3


# write a function that splits s3 uri into bucket and key
def parse_s3_uri(s3_uri):
    """
    Parses the S3 URI and returns the bucket name and key
    """
    s3_uri = s3_uri.replace("s3:/", "")
    bucket_name, key = s3_uri.split("/", 1)
    return bucket_name, key


def download_from_s3(s3_uri, save_dir):
    """
    Downloads a file from s3 to the local file system
    """
    s3 = boto3.client("s3")
    bucket_name, key = parse_s3_uri(s3_uri.as_posix())
    save_path = Path(save_dir) / key
    s3.download_file(bucket_name, key, save_path)
    return save_path
