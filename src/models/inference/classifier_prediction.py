from typing import List

from src.models.inference.base_prediction import BasePrediction
from src.models.inference.representation import BoundingBox
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class Prediction(BasePrediction):
    """
    Data model used to store the predicted values of the model

    Arguments:
        frame (Frame): Frame in which the predictions are made


    """

    def __init__(self, frame: Frame, labels: List[str], scores: List[float],
                 boxes: List[BoundingBox] = None):
        self._boxes = boxes
        self._labels = labels
        self._frame = frame
        self._scores = scores

    @property
    def boxes(self):
        return self._boxes

    @property
    def labels(self):
        return self._labels

    @property
    def frame(self):
        return self._frame

    @property
    def scores(self):
        return self._scores

    @staticmethod
    def predictions_from_batch_and_lists(batch: FrameBatch,
                                         predictions: List[List[str]],
                                         scores: List[List[float]],
                                         boxes: List[
                                             List[BoundingBox]] = None):

        """
        Factory method for returning a list of Prediction objects
        from identified values

        Arguments:
            batch (FrameBatch): frame batch for which the predictions belong to

            predictions (List[List[str]]): List of prediction labels per
            frame in batch

            scores (List[List[float]]): List of prediction scores per frame
            in batch

            boxes (List[List[BoundingBox]]): List of bounding boxes
            associated with predictions

        Returns:
            List[Prediction]
        """
        assert len(batch.frames) == len(predictions)
        assert len(batch.frames) == len(scores)
        if boxes is not None:
            assert len(batch.frames) == len(boxes)

        predictions_ = []
        for i in range(len(batch.frames)):
            prediction_boxes = boxes[i] if boxes is not None else None
            predictions_.append(
                Prediction(batch.frames[i], predictions[i], scores[i],
                           boxes=prediction_boxes))

        return predictions_

    def __eq__(self, other):
        if type(self) is type(other):
            return self.boxes == other.boxes and \
                   self.frame == other.frame and \
                   self.scores == other.scores and \
                   self.labels == other.labels
        return other in self

    def __contains__(self, item):
        return item in self.labels
