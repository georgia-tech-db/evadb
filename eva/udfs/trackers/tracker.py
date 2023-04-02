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
from eva.catalog.catalog_type import NdArrayType
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe


class EVATracker:
    def __init__(self) -> None:
        pass

    @setup(cachable=False, udf_type="object_tracker", batchable=False)
    def setup(self):
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["frame_id", "frame", "bboxes", "scores", "labels"],
                column_types=[
                    NdArrayType.INT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.INT32,
                ],
                column_shapes=[(1,), (None, None, 3), (None, 4), (None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["track_ids", "track_bboxes", "track_scores", "track_labels"],
                column_types=[
                    NdArrayType.INT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                    NdArrayType.INT32,
                ],
                column_shapes=[(None,), (None, 4), (None,), (None,)],
            )
        ],
    )
    def forward(self, df: PandasDataframe) -> PandasDataframe:
        """
        Args:
            df(PandasDataframe): pandas.Dataframe with following columns:
                frame_id (int): the frame id of current frame
                frame (numpy.ndarray): the input frame with shape (C, H, W)
                bboxes (numpy.ndarray): Array of shape `(n, 4)` or of shape `(4,)` where
                each row contains `(xmin, ymin, width, height)`.
                scores (numpy.ndarray): Corresponding scores for each box
                labels (numpy.ndarray): Corresponding labels for each box
        Returns:
            PandasDataframe: pandas.DataFrame with following columns:
                track_ids (numpy.ndarray): Corresponding track id for each box
                track_bboxes (numpy.ndarray):  Array of shape `(n, 4)` of tracked objects
                track_scores (numpy.ndarray): Corresponding scores for each box
                track_labels (numpy.ndarray): Corresponding labels for each box
        """
        raise NotImplementedError
