from enum import Enum
from typing import List

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
        height (int): Height of the image
        width (int): Width of the image
        color_space (ColorSpace): color space of the frame (RGB, HSV, BGR, GRAY)

    """

    def __init__(self, height, width, color_space):
        self._color_space = color_space
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color_space(self):
        return self._color_space

    def __eq__(self, other):
        return self.color_space == other.color_space and \
               self.width == other.width and \
               self.height == other.height



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

    """

    def __init__(self, frames, info):
        self._info = info
        self._frames = tuple(frames)
        self._batch_size = len(frames)

    @property
    def frames(self):
        return self._frames

    @property
    def info(self):
        return self._info
    
    @property
    def batch_size(self):
        return self._batch_size

    def __eq__(self, other):
        return self.info == other.info and \
               self.frames == other.frames


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


class Prediction:
    """
    Data model used to store the predicted values of the model

    Arguments:
        frame (Frame): Frame in which the predictions are made


    """

    def __init__(self, frame: Frame, labels: List[str], boxes: List[BoundingBox] = None):
        self._boxes = boxes
        self._labels = labels
        self._frame = frame

    @property
    def boxes(self):
        return self._boxes

    @property
    def labels(self):
        return self._labels

    @property
    def frame(self):
        return self._frame
