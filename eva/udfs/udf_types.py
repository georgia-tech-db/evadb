from enum import Enum, auto, unique

@unique
class ModelType(Enum):
    ObjectDetection = (auto())
    ActionClassification = (auto())
    FaceRecognition = (auto())