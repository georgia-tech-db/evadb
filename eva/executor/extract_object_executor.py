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
from typing import Iterator

import numpy as np
import pandas as pd
import torch

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.extract_object_plan import ExtractObjectPlan


class ExtractObjectExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ExtractObjectPlan):
        super().__init__(node)
        self.detector = node.detector
        self.tracker = node.tracker
        self.tracker_args = node.tracker_args
        self.node = node

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():
            objects = self.detector.evaluate(batch)
            labels = objects.column_as_numpy_array(self.tracker_args["labels"])
            bboxes = objects.column_as_numpy_array(self.tracker_args["bboxes"])
            scores = objects.column_as_numpy_array(self.tracker_args["scores"])
            if self.need_frames:
                frames = batch.column_as_numpy_array(self.tracker_args["frames"])
            else:
                frames = np.empty([len(bboxes)])
            frame_ids = batch.column_as_numpy_array(self.tracker_args["fids"])
            results = []
            for row in zip(frame_ids, frames, bboxes, scores, labels):
                # mmtracking library needs to concatenate bboxes with scores
                row[2] = torch.cat(
                    [torch.tensor(row[2]), torch.tensor(row[3])[:, None]], axis=1
                )
                # convert labels to integers as strings are not supported by pytorch.
                row[4] = torch.from_numpy(np.array([hash(label) for label in row[4]]))
                track_bboxes, track_labels, ids = self.tracker.track(
                    row[1], row[2], row[4], row[0]
                )
                results.append(
                    {
                        "oids": ids.numpy(),
                        "labels": track_labels.numpy(),
                        "bboxes": track_bboxes.numpy()[:, :-1],
                        "scores": track_bboxes.numpy()[:, -1],
                    }
                )
            outcomes = Batch(pd.DataFrame(results, columns=self.node.output_aliases))
            outcomes = Batch.merge_column_wise([batch, outcomes])
            if self.node.do_unnest:
                outcomes.unnest(self.node.output_aliases)
            outcomes.modify_column_alias(self.node.alias)
            yield outcomes
