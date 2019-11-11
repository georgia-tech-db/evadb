"""
This file defines the interface all dataset loaders need to follow / implement
If any issues arise, please email jaeho.bang@gmail.com

@Jaeho Bang
"""
from abc import ABCMeta, abstractmethod

from src.models import VideoMetaInfo


class AbstractLoader(metaclass=ABCMeta):

    @abstractmethod
    def load_images(self, dir: str):
        pass

    @abstractmethod
    def load_labels(self, dir: str):
        pass

    @abstractmethod
    def load_boxes(self, dir: str):
        pass

    @abstractmethod
    def load_video(self, dir: str):
        pass


class AbstractVideoLoader(metaclass=ABCMeta):
    """
    Abstract class for defining video loader. All other video loaders use this
    abstract class. Video loader are expected fetch the videos from storage
    and return the frames in an iterative manner.

    Attributes:
        video_metadata (VideoMetaInfo): Object containing metadata of the video
        batch_size (int, optional): No. of frames to fetch in batch from video
        skip_frames (int, optional): Number of frames to be skipped
                                     while fetching the video
        offset (int, optional): Start frame location in video
        limit (int, optional): Number of frames needed from the video
    """

    def __init__(self, video_metadata: VideoMetaInfo, batch_size=1,
                 skip_frames=0, offset=None, limit=None):
        self.video_metadata = video_metadata
        self.batch_size = batch_size
        self.skip_frames = skip_frames
        self.offset = offset
        self.limit = limit

    @abstractmethod
    def load(self):
        """
        This is a generator for loading the frames of a video.
         Uses the video metadata and other class arguments

        Yields:
        :obj: `eva.models.FrameBatch`: An object containing a batch of frames
                                       and frame specific metadata
        """
        pass
