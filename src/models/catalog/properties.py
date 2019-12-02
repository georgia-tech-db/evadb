from enum import Enum


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
