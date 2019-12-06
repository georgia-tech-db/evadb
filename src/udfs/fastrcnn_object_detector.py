# Credits: https://github.com/spmallick/learnopencv/blob/master/PyTorch-faster-RCNN/PyTorch_faster_RCNN.ipynb # noqa

from typing import List, Tuple

import numpy as np
import torchvision
from torchvision import transforms

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.inference.classifier_prediction import Prediction
from src.models.inference.representation import BoundingBox, Point
from src.models.storage.batch import FrameBatch
from src.udfs.abstract_udfs import AbstractClassifierUDF


class FastRCNNObjectDetector(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "fastrcnn"

    def __init__(self, threshold=0.5):
        super().__init__()
        self.threshold = threshold
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            pretrained=True)
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle',
            'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
            'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
            'umbrella', 'N/A', 'N/A',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket',
            'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
            'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A',
            'dining table',
            'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote',
            'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
            'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]

    def _get_predictions(self, frames: np.ndarray) -> Tuple[List[List[str]],
                                                            List[List[float]],
                                                            List[List[
                                                                BoundingBox]]]:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need 
            to be performed

        Returns:
            tuple containing predicted_classes (List[List[str]]), 
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])

        """

        transform = transforms.Compose([transforms.ToTensor()])
        images = [transform(frame) for frame in frames]
        predictions = self.model(images)
        prediction_boxes = []
        prediction_classes = []
        prediction_scores = []
        for prediction in predictions:
            pred_class = [str(self.labels[i]) for i in
                          list(prediction['labels'].numpy())]
            pred_boxes = [BoundingBox(Point(i[0], i[1]), Point(i[2], i[3]))
                          for i in
                          list(prediction['boxes'].detach().numpy())]
            pred_score = list(prediction['scores'].detach().numpy())
            pred_t = \
                [pred_score.index(x) for x in pred_score if
                 x > self.threshold][-1]
            pred_boxes = list(pred_boxes[:pred_t + 1])
            pred_class = list(pred_class[:pred_t + 1])
            pred_score = list(pred_score[:pred_t + 1])
            prediction_boxes.append(pred_boxes)
            prediction_classes.append(pred_class)
            prediction_scores.append(pred_score)
        return prediction_classes, prediction_scores, prediction_boxes

    def classify(self, batch: FrameBatch) -> List[Prediction]:
        frames = batch.frames_as_numpy_array()
        (pred_classes, pred_scores, pred_boxes) = self._get_predictions(frames)
        return Prediction.predictions_from_batch_and_lists(batch,
                                                           pred_classes,
                                                           pred_scores, 
                                                           boxes=pred_boxes)
