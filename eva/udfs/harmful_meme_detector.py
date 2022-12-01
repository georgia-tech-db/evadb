from typing import List
import pytesseract
import PIL
from detoxify import Detoxify
import pandas as pd
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
import numpy as np
from torch import Tensor

class HarmfulMemeDetector(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "HarmfulMemeDetector"
    @property
    def labels(self) -> List[str]:
        return [
            "toxic",
            "not toxic",
            "severe_toxicity",
            "obscene",
            "threat",
            "insult",
            "identity_attack"
        ]
    def setup(self, threshold=0.2):
        self.threshold = threshold
        # self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        #     pretrained=True, progress=False
        # )
        # self.model.eval()

    # @property
    # def input_format(self) -> FrameInfo:
    #     return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def forward(self, frames: Tensor):
        print("forward start")

        frames = frames * 255
        frames = np.array(frames, dtype=np.uint8)
        if np.ndim(frames) > 3:
            frames = frames[0]
        image = PIL.Image.fromarray(frames)
        text = pytesseract.image_to_string(image)
        prediction_result = Detoxify('original').predict(text)
        outcome = pd.DataFrame()
        if prediction_result["toxicity"] >= self.threshold:
            outcome = outcome.append("toxic")
        else:
            outcome = outcome.append("not toxic")
        for key in prediction_result.keys():
            if key == "toxicity":
                continue
            if prediction_result[key] >= self.threshold:
                outcome = outcome.append(key)

        print("forward finish")
        return outcome
