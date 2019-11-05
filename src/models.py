from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Callable

import numpy as np


class ColorSpace(Enum):
    RGB = 1
    HSV = 2
    BGR = 3
    GRAY = 4


class VideoFormat(Enum):
    MOV = 1
    WMV = 2
    OGG = 3
    AVI = 4
    FLV = 5
    MP4 = 6
    MPEG = 7


class VideoMetaInfo:
    """
    Data model used for storing video related information
    # TODO: This is database metadata. Need to discuss what goes in here

    Arguments:
        file (str): path where the video is stored
        fps (int): Frames per second in the video
        c_format (VideoFormat): Video File Format

    """

    def __init__(self, file, fps, c_format):
        self._fps = fps
        self._file = file
        self._c_format = c_format

    @property
    def file(self):
        return self._file

    @property
    def fps(self):
        return self._fps

    @property
    def c_format(self):
        return self._c_format


class FrameInfo:
    """
    Data model contains information about the frame

    Arguments:
        height (int)(default: -1): Height of the image : left as -1 when the height of the frame is not required
        width (int)(default: -1): Width of the image : left as -1 when the height of the frame is not required
        channels (int)(default: 3): Number of input channels in the video
        color_space (ColorSpace)(default: ColorSpace.RGB): color space of the frame (RGB, HSV, BGR, GRAY)

    """

    def __init__(self, height=-1, width=-1, channels=3, color_space=ColorSpace.RGB):
        self._color_space = color_space
        self._width = width
        self._height = height
        self._channels = channels

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color_space(self):
        return self._color_space

    @property
    def channels(self):
        return self._channels

    def __eq__(self, other):
        return self.color_space == other.color_space and \
               self.width == other.width and \
               self.height == other.height and \
               self.channels == other.channels


class Frame:
    """
    Data model used for storing video frame related information

    Arguments:
        index (int): The index of the frame in video
        data (numpy.ndarray): Frame object from video
        info (FrameInfo): Contains properties of the frame

    """

    def __init__(self, index, data, info):
        self._data = data
        self._index = index
        self._info = info

    @property
    def data(self):
        return self._data

    @property
    def index(self):
        return self._index

    @property
    def info(self):
        return self._info

    def __eq__(self, other):
        return self.index == other.index and \
               np.array_equal(self.data, other.data) and \
               self.info == other.info


class FrameBatch:
    """
    Data model used for storing a batch of frames

    Arguments:
        frames (List[Frame]): List of video frames
        info (FrameInfo): Information about the frames in the batch
        outcomes (Dict[str, List[BasePrediction]]): outcomes of running a udf with name 'x' as key

    """

    def __init__(self, frames, info, outcomes=None):
        super().__init__()
        if outcomes is None:
            outcomes = dict()
        self._info = info
        self._frames = tuple(frames)
        self._batch_size = len(frames)
        self._outcomes = outcomes

    @property
    def frames(self):
        return self._frames

    @property
    def info(self):
        return self._info

    @property
    def batch_size(self):
        return self._batch_size

    def frames_as_numpy_array(self):
        return np.array([frame.data for frame in self.frames])

    def __eq__(self, other):
        return self.info == other.info and \
               self.frames == other.frames and \
               self._outcomes == other._outcomes

    def set_outcomes(self, name, predictions: 'BasePrediction'):
        """
        Used for storing outcomes of the UDF predictions

        Arguments:
            name (str): name of the UDF to which the predictions belong to
            predictions (BasePrediction): Predictions/Outcome after executing the UDF on prediction

        """
        self._outcomes[name] = predictions

    def get_outcomes_for(self, name: str) -> List['BasePrediction']:
        """
        Returns names corresponding to a name
        Arguments:
            name (str): name of the udf on which predicate is being executed

        Returns:
            List[BasePrediction]
        """
        return self._outcomes.get(name, [])

    def _get_frames_from_indices(self, required_frame_ids):
        # TODO: Implement this using __getitem__
        new_frames = [self.frames[i] for i in required_frame_ids]
        new_batch = FrameBatch(new_frames, self.info)
        for key in self._outcomes:
            new_batch._outcomes[key] = [self._outcomes[key][i] for i in required_frame_ids]
        return new_batch

    def __getitem__(self, indices) -> 'FrameBatch':
        """
        Takes as input the slice for the list
        Arguments:
            item (list or Slice):

        :return:
        """
        if type(indices) is list:
            return self._get_frames_from_indices(indices)
        elif type(indices) is slice:
            start = indices.start if indices.start else 0
            end = indices.stop if indices.stop else len(self.frames)
            if end < 0:
                end = len(self.frames) + end
            step = indices.step if indices.step else 1
            return self._get_frames_from_indices(range(start, end, step))


class Point:
    """
    Data model used for storing the point in coordinate space

    Arguments:
        x (int): x coordinate
        y (int): y coordinate
    """

    def __init__(self, x, y):
        self._y = y
        self._x = x

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __eq__(self, other):
        return self.x == other.x and \
               self.y == other.y


class BoundingBox:
    """
    Data model used for storing bounding box

    Arguments:
        top_left (Point): Top left point of the bounding box
        bottom_right (Point): Bottom right point of the bounding box

    """

    def __init__(self, top_left: Point, bottom_right: Point):
        self._bottom_right = bottom_right
        self._top_left = top_left

    @property
    def bottom_right(self):
        return self._bottom_right

    @property
    def top_left(self):
        return self._top_left

    def __eq__(self, other):
        return self.bottom_right == other.bottom_right and \
               self.top_left == other.top_left


class BasePrediction(ABC):
    """Base class for any type of prediction from model"""

    @abstractmethod
    def eq(self, element) -> bool:
        """
        Checks if prediction is equal to the element
        Arguments:
            element (object): Check if element is equivalent
        Returns:
            bool (True if equal else False)
        """
        pass

    @abstractmethod
    def contains(self, element) -> bool:
        """
        Checks if the prediction contains the element
        Arguments:
            element (object): Element to be checked
        Returns:
            bool (True if contains else False)
        """
        pass

    @abstractmethod
    def has_one(self, elements: List[object]) -> bool:
        """
        This method is used for defining the 'IN' operation
        Arguments:
            elements (List[object]): if the predictions are in the given list
        Returns:
            bool
        """
        pass


class Prediction(BasePrediction):
    """
    Data model used to store the predicted values of the model

    Arguments:
        frame (Frame): Frame in which the predictions are made


    """

    def __init__(self, frame: Frame, labels: List[str], scores: List[float], boxes: List[BoundingBox] = None):
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
    def predictions_from_batch_and_lists(batch: FrameBatch, predictions: List[List[str]],
                                         scores: List[List[float]], boxes: List[List[BoundingBox]] = None):

        """
        Factory method for returning a list of Prediction objects from identified values

        Arguments:
            batch (FrameBatch): frame batch for which the predictions belong to
            predictions (List[List[str]]): List of prediction labels per frame in batch
            scores (List[List[float]]): List of prediction scores per frame in batch
            boxes (List[List[BoundingBox]]): List of bounding boxes associated with predictions

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
            predictions_.append(Prediction(batch.frames[i], predictions[i], scores[i], boxes=prediction_boxes))

        return predictions_

    def __eq__(self, other):
        return self.boxes == other.boxes and \
               self.frame == other.frame and \
               self.scores == other.scores and \
               self.labels == other.labels

    def eq(self, element) -> bool:
        return self.contains(element)

    def has_one(self, element: List[object]) -> bool:
        pass

    def contains(self, element) -> bool:
        return element in self.labels


class Predicate:
    """
    Used for representing the predicates in case of filter operation.

    Arguments:
        name (str): Name of the field on which predicate needs to be executed
        predicate (lambda)
    """

    def __init__(self, name, predicate: Callable[[BasePrediction], bool]):
        self._name = name
        self._predicate = predicate

    @property
    def name(self):
        return self._name

    def __call__(self, prediction: BasePrediction):
        return self._predicate(prediction)
