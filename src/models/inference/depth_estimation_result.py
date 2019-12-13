from src.models.storage.frame import Frame
from src.models.storage.batch import FrameBatch
from src.models.inference.base_prediction import BasePrediction
from typing import List, Tuple
import numpy as np


class DepthEstimationResult(BasePrediction):
    """
    Data model used to store the result of the depth estimation model

    Arguments:
        frame (Frame): Frame in which the predictions are made
        segm (np.ndarray) : Segmentations estimated in the image
        depth (np.ndarray) : Depth values estimated in the image

    """

    def __init__(self, frame: Frame, segm: np.ndarray, depth: np.ndarray):
        self._frame = frame
        self._segm = segm
        self._depth = depth

    # stores the depth value for the frame
    @property
    def depth(self):
        return self._depth

    # stores the frame
    @property
    def frame(self):
        return self._frame

    # stores the segmentation value for the frame
    @property
    def segm(self):
        return self._segm

    @staticmethod
    def depth_estimation_result_from_batch_and_lists(
            batch: FrameBatch, segms: List[np.ndarray],
            depths: List[np.ndarray]):
        """
        Factory method for returning a list of depth estimation result for the
        batch

        Arguments:
            batch (FrameBatch): frame batch for which the predictions belong
            to segms (List[numpy.ndarray]): List of segmentation output per
            frame in batch depths (List[numpy.ndarray]): List of depth
            estimation per frame in batch

        Returns:
            List[DepthEstimationResult]
        """
        # length of frame batch should be equal to length of segmentation and
        # depth arrays
        assert len(batch.frames) == len(segms)
        assert len(batch.frames) == len(depths)
        results = []

        # iterate over each frame and the depth/segmentation results to create
        # a list of DepthEstimationResult objects
        for i in range(len(batch.frames)):
            results.append(DepthEstimationResult(
                batch.frames[i], segms[i], depths[i]))

        return results
