from typing import List
import pytesseract
import PIL
from detoxify import Detoxify
import pandas as pd
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
import numpy as np
from torch import Tensor
from eva.utils.logging_manager import logger
from eva.models.catalog.frame_info import FrameInfo
from torchvision.transforms import Compose, ToTensor, Normalize, Grayscale
from PIL import Image

class HarmfulMemeDetector(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "HarmfulMemeDetector"
    
    def setup(self, threshold=0.2):
        logger.warn("setup start")
        self.threshold = threshold
        self.model = Detoxify('original')
        logger.warn("setup finish")
    
    @property
    def input_format(self) -> FrameInfo:
        logger.warn("input_format start")
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)
    
    @property
    def labels(self) -> List[str]:
        logger.warn("labels start")
        return [
            "toxic",
            "not toxic"
        ]

    def forward(self, frames: np.ndarray) -> pd.DataFrame:
        # reconstruct dimension of the input
        frames_list = frames.values.tolist()
        frames = np.array(frames_list)[0][0]

        image = PIL.Image.fromarray(frames.astype('uint8'), 'RGB')
        text = pytesseract.image_to_string(image)
        logger.warn(text)
        prediction_result = self.model.predict(text)
        outcome = pd.DataFrame()
        if prediction_result["toxicity"] >= self.threshold:
            outcome = outcome.append({"labels": "toxic"}, ignore_index=True)
        else:
            outcome = outcome.append({"labels": "not toxic"}, ignore_index=True)
        return outcome
