import itertools
import numpy as np
import pandas as pd
import cv2
import os

from PIL import Image
from typing import List
from math import sqrt

import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torchvision import models

from torchvision.transforms import Compose, transforms

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.pytorch_abstract_udf import PytorchAbstractUDF


class VGG16FeatureExtractorUDF(PytorchAbstractUDF):
	@property
	def name(self) -> str:
		return "VGG16 Feature Extractor"
	
	@property
	def transforms(self) -> Compose:
		return Compose([
			transforms.Resize([200,200]),
			transforms.ToTensor()
		])
	@property
	def labels(self) -> List[str]:
		return []
	@property
	def input_format(self) -> FrameInfo:
		return FrameInfo(-1,-1,3, ColorSpace.RGB)
	def __init__(self):
		super().__init__()
		self.model = models.vgg16(pretrained = True)
		for param in self.model.parameters():
			param.requires_grad = False

	def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
		descriptors = pd.DataFrame()
		for f in frames:
			with torch.no_grad():
				descriptors = descriptors.append({"descriptors": np.array(self.model.features(torch.unsqueeze(f, 0))).astype('float32')}, ignore_index=True)
		return descriptors

	def classify(self, frames: Tensor) -> pd.DataFrame:
		return self._get_predictions(frames)
        
