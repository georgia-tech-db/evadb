
import numpy as np
import pandas as pd
import torch
from PIL.Image import Image

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from typing import List

try:
    from torch import Tensor
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )

try:
    import torchvision
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )

class CarPlateDetector(PytorchAbstractClassifierUDF):
    @property
    def name(self) -> str:
        return "car_plate"

    def setup(self, threshold=0.1):
        self.threshold = threshold
        self.model = torchvision.models.segmentation.deeplabv3_resnet101(
        pretrained=True, progress=True, aux_loss=False)
        for p in self.model.parameters():
            p.requires_grad = False

        outputchannels = 1
        self.model.classifier = torchvision.models.segmentation.deeplabv3.DeepLabHead(
            2048, outputchannels)

        model_path = './model.pth'
        checkpoint = torch.load(model_path, map_location='cpu')
        self.model.load_state_dict(checkpoint['model'])
        self.model.eval()

        if torch.cuda.is_available():
            self.model.to('cuda')

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return ["car plate"]

    def pred(self, image, model):
        preprocess = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0)

        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            model.to('cuda')

        with torch.no_grad():
            output = model(input_batch)['out'][0]
            return output

    def forward(self, frames: Tensor):
        outcome = pd.DataFrame()
        for frame in frames:
            image = torchvision.transforms.ToPILImage()(frame)
            output = self.pred(image, self.model)
            mask = output.cpu().numpy()[0] > 0.1
            mask = mask.astype(np.uint8)
            outcome = outcome.append({"results": mask}, ignore_index=True)
        return outcome



