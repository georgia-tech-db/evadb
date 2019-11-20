from src.models import FrameBatch, Frame
from typing import List, Tuple

import numpy as np

class DepthEstimationResult:
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

    @property
    def depth(self):
        return self._depth

    @property
    def frame(self):
        return self._frame

    @property
    def segm(self):
        return self._segm

    @staticmethod
    def depth_estimation_result_from_batch_and_lists(batch: FrameBatch, segms: List[np.ndarray],
                                         depths: List[np.ndarray]):

        """
        Factory method for returning a list of depth estimation result for the batch

        Arguments:
            batch (FrameBatch): frame batch for which the predictions belong to
            segms (List[numpy.ndarray]): List of segmentation output per frame in batch
            depths (List[numpy.ndarray]): List of depth estimation per frame in batch

        Returns:
            List[DepthEstimationResult]
        """
        assert len(batch.frames) == len(segms)
        assert len(batch.frames) == len(depths)
        results = []
        for i in range(len(batch.frames)):
            results.append(DepthEstimationResult(batch.frames[i], segms[i], depths[i]))

        return results

