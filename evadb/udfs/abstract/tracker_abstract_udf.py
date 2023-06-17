# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import typing

import numpy
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe


class EvaDBTrackerAbstractUDF(AbstractUDF):
    """
    An abstract class for all EvaDB object trackers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @setup(cacheable=False, udf_type="object_tracker", batchable=False)
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["frame_id", "frame", "bboxes", "scores", "labels"],
                column_types=[
                    NdArrayType.INT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.STR,
                ],
                column_shapes=[(1,), (None, None, 3), (None, 4), (None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["track_ids", "track_labels", "track_bboxes", "track_scores"],
                column_types=[
                    NdArrayType.INT32,
                    NdArrayType.INT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,), (None,), (None, 4), (None,)],
            )
        ],
    )
    def forward(
        self,
        frame_id: numpy.ndarray,
        frame: numpy.ndarray,
        labels: numpy.ndarray,
        bboxes: numpy.ndarray,
        scores: numpy.ndarray,
    ) -> typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]:
        """
        Args:
            frame_id (numpy.ndarray): the frame id of current frame
            frame (numpy.ndarray): the input frame with shape (C, H, W)
            labels (numpy.ndarray): Corresponding labels for each box
            bboxes (numpy.ndarray): Array of shape `(n, 4)` or of shape `(4,)` where
            each row contains `(xmin, ymin, width, height)`.
            scores (numpy.ndarray): Corresponding scores for each box
        Returns:
            track_ids (numpy.ndarray): Corresponding track id for each box
            track_labels (numpy.ndarray): Corresponding labels for each box
            track_bboxes (numpy.ndarray):  Array of shape `(n, 4)` of tracked objects
            track_scores (numpy.ndarray): Corresponding scores for each box
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        assert isinstance(
            args[0], pd.DataFrame
        ), f"Expecting pd.DataFrame, got {type(args[0])}"

        results = []
        for _, row in args[0].iterrows():
            tuple = (
                numpy.array(row[0]),
                numpy.array(row[1]),
                numpy.stack(row[2]),
                numpy.stack(row[3]),
                numpy.stack(row[4]),
            )
            results.append(self.forward(*tuple))
        return pd.DataFrame(
            results,
            columns=["track_ids", "track_labels", "track_bboxes", "track_scores"],
        )
