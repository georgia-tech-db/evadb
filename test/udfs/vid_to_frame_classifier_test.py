from src.udfs import video_action_classification
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
import numpy as np
import unittest


class VidToFrameClassifier_Test(unittest.TestCase):

    def test_VidToFrameClassifier(self):
        model = video_action_classification.VideoToFrameClassifier()
        assert model is not None
        
        X = np.random.random([240, 320, 3])
        model.classify(FrameBatch([Frame(0, X, None)], None))