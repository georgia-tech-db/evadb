import os
import unittest

import cv2

from src.models import Frame, FrameBatch
from src.udfs.fastrcnn_object_detector import FastRCNNObjectDetector

NUM_FRAMES = 10


class FastRCNNObjectDetectorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def _load_image(self, path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @unittest.skip("torchvision correct version needed")
    def test_should_return_batches_equivalent_to_number_of_frames(self):
        frame_dog = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'dog.jpeg')), None)
        frame_dog_cat = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'dog_cat.jpg')), None)
        frame_batch = FrameBatch([frame_dog, frame_dog_cat], None)
        detector = FastRCNNObjectDetector()
        result = detector.classify(frame_batch)

        self.assertEqual(["dog"], result[0].labels)
        self.assertEqual(["cat", "dog"], result[1].labels)
