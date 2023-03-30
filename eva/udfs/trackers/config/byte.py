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

# modified init_track_thr = 0.0, so that we get track for each detection
img_scale = (800, 1440)
samples_per_gpu = 4

model = dict(
    type="ByteTrack",
    detector=dict(
        input_size=img_scale,
        random_size_range=(18, 32),
        bbox_head=dict(num_classes=1),
        test_cfg=dict(score_thr=0.01, nms=dict(type="nms", iou_threshold=0.7)),
        init_cfg=dict(
            type="Pretrained",
            checkpoint="https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_x_8x8_300e_coco/yolox_x_8x8_300e_coco_20211126_140254-1ef88d67.pth",  # noqa: E251  # noqa: E501
        ),
    ),
    motion=dict(type="KalmanFilter"),
    tracker=dict(
        type="ByteTracker",
        obj_score_thrs=dict(high=0.6, low=0.1),
        init_track_thr=0.6,
        weight_iou_with_det_scores=True,
        match_iou_thrs=dict(high=0.1, low=0.5, tentative=0.3),
        num_frames_retain=30,
    ),
)
