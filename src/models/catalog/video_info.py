from src.models.catalog.properties import VideoFormat


class VideoMetaInfo:
    """
    Data model used for storing video related information
    # TODO: This is database metadata. Need to discuss what goes in here

    Arguments:
        file (str): path where the video is stored
        fps (int): Frames per second in the video
        c_format (VideoFormat): Video File Format

    """

    def __init__(self, file: str, fps: int, c_format: VideoFormat, compressed=False, compressed_index = None, original_path = None):
        self._fps = fps
        self._file = file
        self._c_format = c_format
        self._compressed = compressed
        self._compressed_index = compressed_index
        self._original_path = original_path 

    @property
    def file(self) -> str:
        return self._file

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def c_format(self) -> VideoFormat:
        return self._c_format

    @property
    def compressed(self) -> bool:
        return self._compressed
    
    @property
    def compressed_index(self) -> list:
        return self._compressed_index

    @property
    def original_path(self) -> str:
        return self._original_path