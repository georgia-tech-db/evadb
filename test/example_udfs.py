import numpy as np
import pandas as pd

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.inference.outcome import Outcome
from src.udfs.abstract_udfs import AbstractClassifierUDF
from typing import List

class DummyObjectDetector(AbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "dummyObjectDetector"

    def __init__(self):
        super().__init__()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return ['__background__', 'person', 'bicycle']

    def classify(self, frames: np.ndarray) -> List[Outcome]:
        if (frames == np.array(np.ones((2, 2, 3)) * 0.1 * float(5 + 1) * 255,
                               dtype=np.uint8)).all():
            label = self.labels[1]
        else:
            label = self.labels[2]
        prediction_df_list = [Outcome(
            pd.DataFrame([{'label': [label, 'apple']}]), 'label')]
        return prediction_df_list
