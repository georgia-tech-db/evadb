
from typing import List

import pandas as pd
import numpy as np
import os
import torchvision
import torch
import torch.nn as nn
import torch.nn.functional as F
from eva.utils.logging_manager import logger

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from torch import Tensor
from torchvision import models
from torchvision.transforms import Compose, ToTensor, Resize
from PIL import Image
import sys

pytorch3dpath = "./EfficientNet-PyTorch-3D"
sys.path.append(pytorch3dpath)
from efficientnet_pytorch_3d import EfficientNet3D

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = EfficientNet3D.from_name("efficientnet-b0", override_params={'num_classes': 2}, in_channels=1)
        n_features = self.net._fc.in_features
        self.net._fc = nn.Linear(in_features=n_features, out_features=1, bias=True)
    
    def forward(self, x):
        out = self.net(x)
        return out

class MRIClassifier(PytorchAbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "MRIClassifier"

    def setup(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Model()
        checkpoint = torch.load("FLAIR-e10-loss0.680-auc0.624.pth", map_location=device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            'mgmt'
        ]

    def pred(self, image, model):
        img_arr = [image for i in range(64)]
        composed = Compose([
            torchvision.transforms.Grayscale(num_output_channels=1),
            Resize((256, 256)),            
            ToTensor(),
            # torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            # torchvision.transforms.Normalize(mean=[0.485],std=[0.229] )
        ])
        input_batch = [composed(i) for i in img_arr]
        img3d = np.stack(input_batch).T
        
        logger.warning(img3d.shape)

        img3d = img3d.reshape((1,256, 256,64))
        img3d = np.expand_dims(img3d, axis=0)
        x= torch.tensor(img3d).float()

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        with torch.no_grad():
            tmp_pred = torch.sigmoid(model(x.to(device))).cpu().numpy().squeeze()

        return tmp_pred.tolist()


    def forward(self, frames: Tensor):
        outcome = pd.DataFrame()
        
        for frame in frames:
            image = torchvision.transforms.ToPILImage()(frame)
            output = self.pred(image, self.model)
            pred = int(np.round(output))
            outcome = outcome.append({"results": pred}, ignore_index=True)
        return outcome