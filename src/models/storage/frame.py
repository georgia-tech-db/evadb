import numpy as np


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
