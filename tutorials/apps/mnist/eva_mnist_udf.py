import pandas as pd
from torch import Tensor

from eva.udfs.pytorch_abstract_udf import PytorchAbstractUDF
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from mnist_raw_script import mnist
from torchvision.transforms import Compose, ToTensor, Normalize


class MnistCNN(PytorchAbstractUDF):

    @property
    def name(self) -> str:
        return 'MnistCNN'

    def __init__(self):
        super().__init__()
        self.model = mnist()
        self.mode.eval()

    @property
    def input_format(self):
        return FrameInfo(1, 28, 28, ColorSpace.RGB)

    @property
    def labels(self):
        return list([str(num) for num in range(10)])

    def transforms(self) -> Compose:
        return Compose([
            ToTensor(),
            Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        outcome = pd.DataFrame()
        outcome['label'] = self.model(frames)
        return outcome
