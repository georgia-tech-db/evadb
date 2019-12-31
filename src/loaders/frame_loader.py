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
from pyspark.sql.types import IntegerType

from petastorm.codecs import ScalarCodec
from petastorm.codecs import CompressedImageCodec
from petastorm.codecs import CompressedNdarrayCodec
from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm.unischema import dict_to_spark_row, Unischema, UnischemaField

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
from tensorflow.python.debug.examples.debug_mnist import NUM_LABELS


class FrameLoader():
    def __init__(
            self,
            dataset_name: str,
            frame_metadata: FrameInfo,
            *args,
            **kwargs):
        super().__init__(frame_metadata, *args, **kwargs)

        dataset_schema_name = dataset_name + 'Schema'
        H = frame_metadata.height
        W = frame_metadata.width
        C = frame_metadata.num_channels
        NUM_LABELS = 5

        # The schema defines how the dataset schema looks like
        FrameDatasetSchema = Unischema(dataset_schema_name, [
            UnischemaField('frame_id', np.int32, (),
                           ScalarCodec(IntegerType()), False),
            UnischemaField('frame_data', np.uint8, (H, W, C),
                           CompressedNdarrayCodec(), False),
            UnischemaField('frame_labels', np.float16,
                           (NUM_LABELS, None, None, None),
                           CompressedNdarrayCodec(), False),
        ])

        output_url = 'file:///tmp/hello_world_dataset'
        rowgroup_size_mb = 256

        spark = SparkSession.builder.config(
            'spark.driver.memory',
            '2g').master('local[2]').getOrCreate()
        sc = spark.sparkContext

        # Wrap dataset materialization portion.
        # Will take care of setting up spark environment variables as
        # well as save petastorm specific metadata
        rows_count = 10
        with materialize_dataset(spark,
                                 output_url,
                                 FrameDatasetSchema,
                                 rowgroup_size_mb):

            rows_rdd = sc.parallelize(range(rows_count))\
                .map(row_generator)\
                .map(lambda x: dict_to_spark_row(FrameDatasetSchema, x))

            spark.createDataFrame(rows_rdd,
                                  FrameDatasetSchema.as_spark_schema()) \
                .coalesce(10) \
                .write \
                .mode('overwrite') \
                .parquet(output_url)

    def load_images(self):
