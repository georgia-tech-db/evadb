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
from pathlib import Path
from test.util import EVA_TEST_DATA_DIR
from unittest.mock import patch

import cv2
import pandas as pd

from eva.models.storage.batch import Batch

NUM_FRAMES = 10


class FaceNet(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = Path(EVA_TEST_DATA_DIR) / "data" / "facenet"

    def _load_image(self, path):
        assert path.exists(), f"File does not exist at the path {str(path)}"
        img = cv2.imread(str(path))
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        from eva.udfs.face_detector import FaceDetector

        single_face_img = Path("data/facenet/one.jpg")
        multi_face_img = Path("data/facenet/multiface.jpg")
        frame_single_face = {
            "id": 1,
            "data": self._load_image(single_face_img),
        }
        frame_multifaces = {
            "id": 2,
            "data": self._load_image(multi_face_img),
        }
        frame_batch = Batch(pd.DataFrame([frame_single_face, frame_single_face]))
        detector = FaceDetector()
        result = detector(frame_batch.project(["data"]).frames)
        self.assertEqual(1, len(result.iloc[0]["bboxes"]))
        self.assertEqual(1, len(result.iloc[1]["bboxes"]))

        frame_batch = Batch(pd.DataFrame([frame_multifaces]))
        detector = FaceDetector()
        result = detector(frame_batch.project(["data"]).frames)
        self.assertEqual(6, len(result.iloc[0]["bboxes"]))

    @unittest.skip("Needs GPU")
    def test_should_run_on_gpu(self):
        from eva.udfs.face_detector import FaceDetector

        single_face_img = Path("data/facenet/one.jpg")
        frame_single_face = {
            "id": 1,
            "data": self._load_image(single_face_img),
        }
        frame_batch = Batch(pd.DataFrame([frame_single_face, frame_single_face]))

        # test on GPU
        detector = FaceDetector().to_device(0)
        result = detector(frame_batch.project(["data"]).frames)
        self.assertEqual(6, len(result.iloc[0]["bboxes"]))

    def test_mock_to_device(self):
        device = 10
        from eva.udfs.face_detector import FaceDetector

        with patch("eva.udfs.face_detector.MTCNN") as mock_mtcnn:
            with patch("eva.udfs.face_detector.torch") as mock_torch:
                mock_torch.device.return_value = "cuda:10"
                detector = FaceDetector()
                detector = detector.to_device(device)
                mock_torch.device.assert_called_once()
            mock_mtcnn.assert_called_with(device=f"cuda:{device}")
