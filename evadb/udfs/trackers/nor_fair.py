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
import numpy as np

from evadb.udfs.abstract.tracker_abstract_udf import EvaDBTrackerAbstractUDF
from evadb.utils.generic_utils import try_to_import_norfair
from evadb.utils.math_utils import get_centroid

DISTANCE_THRESHOLD_CENTROID: int = 30


class NorFairTracker(EvaDBTrackerAbstractUDF):
    @property
    def name(self) -> str:
        return "NorFairTracker"

    def setup(self, distance_threshold=DISTANCE_THRESHOLD_CENTROID) -> None:
        # https://github.com/tryolabs/norfair/blob/74b11edde83941dd6e32bcccd5fa849e16bf8564/norfair/tracker.py#L18
        try_to_import_norfair()
        from norfair import Tracker

        self.tracker = Tracker(
            distance_function="euclidean",
            distance_threshold=distance_threshold,
        )
        self.prev_frame_id = None

    def forward(self, frame_id, frame, labels, bboxes, scores):
        from norfair import Detection

        norfair_detections = [
            Detection(
                points=get_centroid(bbox),
                scores=np.array([score]),
                label=hash(label) % 10**8,
                data=(label, bbox, score),
            )
            for (bbox, score, label) in zip(bboxes, scores, labels)
        ]

        # calculate jump between consecutive update calls
        period = frame_id - self.prev_frame_id if self.prev_frame_id else 1
        self.prev_frame_id = frame_id

        # call tracker
        tracked_objects = self.tracker.update(
            detections=norfair_detections, period=period
        )
        bboxes_xyxy = []
        labels = []
        scores = []
        ids = []
        for obj in tracked_objects:
            det = obj.last_detection.data
            labels.append(det[0])
            bboxes_xyxy.append(det[1])
            scores.append(det[2])
            ids.append(obj.id)

        return np.array(ids), np.array(labels), np.array(bboxes_xyxy), np.array(scores)
