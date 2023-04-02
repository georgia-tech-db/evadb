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
import pandas as pd
from norfair import Detection, Tracker

from eva.udfs.trackers.tracker import EVATracker
from eva.utils.math_utils import get_centroid

DISTANCE_THRESHOLD_CENTROID: int = 30


class NorFairTracker(EVATracker):
    def __init__(self, distance_threshold=DISTANCE_THRESHOLD_CENTROID) -> None:
        # https://github.com/tryolabs/norfair/blob/74b11edde83941dd6e32bcccd5fa849e16bf8564/norfair/tracker.py#L18
        self.tracker = Tracker(
            distance_function="euclidean",
            distance_threshold=distance_threshold,
        )

    def forward(self, df):
        norfair_detections = (
            Detection(
                points=get_centroid(df["bboxes"].to_numpy()),
                scores=df["scores"].to_numpy(),
                label=df["labels"].to_numpy(),
            ),
        )

        tracked_objects = self.tracker.update(detections=norfair_detections)
        bboxes_xyxy = []
        labels = []
        scores = []
        ids = []
        for obj in tracked_objects:
            det = obj.last_detection.data
            bboxes_xyxy.append(det[:4])
            labels.append(int(det[-1]))
            scores.append(int(det[-2]))
            ids.append(obj.id)

        results = pd.DataFrame(
            [ids, bboxes_xyxy, scores, labels],
            columns=["track_ids", "track_bboxes", "track_scores", "track_labels"],
        )
        return results
