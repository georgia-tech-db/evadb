
import pandas as pd
import numpy as np
import easyocr


from typing import List
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.abstract_udfs import AbstractClassifierUDF
from src.udfs.gpu_compatible import GPUCompatible


class OpticalCharacterRecognition(AbstractClassifierUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "opticalcharacterrecognition"

    def to_device(self, device: str):
        """

        :param device:
        :return:
        """
        self.model = easyocr.Reader(['en'], gpu = "cuda:{}".format(device))
        return self
    
    
    def __init__(self, threshold=0.85):
        super().__init__()
        self.threshold = threshold
        self.model = easyocr.Reader(['en'])


    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)


    @property
    def labels(self) -> List[str]:
        """
            Empty as there are no labels required for
            optical character recognition
        """
        return

    def classify(self, frames: np.ndarray) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (tensor): Frames on which OCR needs
            to be performed

        Returns:
            tuple containing predicted_classes (List[List[str]]),
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])

        """
        
        frames_list = frames.values.tolist()
        frames = np.array(frames_list)

        outcome = pd.DataFrame()
        
        for i in range(frames.shape[0]):
            prediction = self.model.readtext_batched(frames[i])
            
            prediction = np.array(prediction)

            pred_class = []
            pred_boxes = []
            pred_score = []

            if prediction.size != 0:
                for detection in prediction:

                    pred_class.append(detection[0][1])
                    pred_boxes.append([[detection[0][0][0], detection[0][0][1]],
                            [detection[0][0][2], detection[0][0][3]]])
                    pred_score.append(detection[0][2])
                
                pred_t = \
                    [pred_score.index(x) for x in pred_score if
                    x > self.threshold]

                pred_t = np.array(pred_t)
                
                if pred_t.size != 0:
                    pred_class = np.array(pred_class)
                    pred_class = pred_class[pred_t]
                    
                    pred_boxes = np.array(pred_boxes)
                    pred_boxes = pred_boxes[pred_t]

                    pred_score = np.array(pred_score)
                    pred_score = pred_score[pred_t]

                    outcome = outcome.append(
                        {
                            "labels": list(pred_class),
                            "scores": list(pred_score),
                            "boxes": list(pred_boxes)
                        },
                        ignore_index=True)


        return outcome