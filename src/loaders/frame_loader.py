# coding=utf-8
# Copyright 2018-2020 EVA
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

import numpy as np
import os
from pyspark.sql.types import IntegerType

from petastorm.codecs import ScalarCodec
from petastorm.codecs import CompressedNdarrayCodec
from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm.unischema import dict_to_spark_row, Unischema, UnischemaField

from src.models.catalog.frame_info import FrameInfo
from src.spark.session import Session

from src.utils.logging import Logger

EVA_DATASETS_DIR = "file:///tmp/eva_dataset"


def row_generator(x, H, W, C):
    """Returns a single entry in the generated dataset.
    Return a bunch of random values as an example."""
    return {'frame_id': x,
            'frame_data': np.random.randint(0, 10,
                                            dtype=np.uint8, size=(H, W, C))}


class FrameLoader():
    def __init__(
            self,
            dataset_name: str,
            frame_metadata: FrameInfo):

        self.dataset_name = dataset_name
        self.H = frame_metadata.height
        self.W = frame_metadata.width
        self.C = frame_metadata.num_channels

        # The schema defines how the dataset schema looks like
        self.dataset_schema = Unischema(self.dataset_name, [
            UnischemaField('frame_id', np.int32, (),
                           ScalarCodec(IntegerType()), False),
            UnischemaField('frame_data', np.uint8, (self.H, self.W, self.C),
                           CompressedNdarrayCodec(), False),
        ])

        # Construct output location
        output_url = os.path.join(EVA_DATASETS_DIR, self.dataset_name)
        print(output_url)
        rowgroup_size_mb = 256

        # Get session handle
        session = Session()
        spark = session.get_session()
        spark_context = session.get_context()

        # Wrap dataset materialization portion.
        rows_count = 10
        with materialize_dataset(spark,
                                 output_url,
                                 self.dataset_schema,
                                 rowgroup_size_mb):

            rows_rdd = spark_context.parallelize(range(rows_count))\
                .map(lambda x: row_generator(x, self.H, self.W, self.C))\
                .map(lambda x: dict_to_spark_row(self.dataset_schema, x))

            spark.createDataFrame(rows_rdd,
                                  self.dataset_schema.as_spark_schema()) \
                .coalesce(10) \
                .write \
                .mode('overwrite') \
                .parquet(output_url)

    def load_images(self):

        Logger().log("Load Images")
