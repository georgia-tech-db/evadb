# Credits: https://github.com/spmallick/learnopencv/blob/master/PyTorch-faster-RCNN/PyTorch_faster_RCNN.ipynb # noqa
import torch
from torch import nn
import torchvision

import torch.optim as optim
import torch.nn.functional as F

import torchvision.transforms as transforms
from torch.autograd import Variable

from torch.utils.data import Dataset, DataLoader

import glob
import os.path as osp

import os
import skvideo
from skvideo import io as vp
from time import time

import argparse
import numpy as np
import pandas as pd

import random
import math
import numbers
import collections
from PIL import Image, ImageOps
try:
    import accimage
except ImportError:
    accimage = None
from typing import List, Tuple

spatial_transform = Compose([
    MultiScaleRandomCrop(scales, 100),
    RandomHorizontalFlip(),
    ToTensor(), Normalize([0, 0, 0], [1, 1, 1])
])

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.inference.classifier_prediction import Prediction
from src.models.inference.representation import BoundingBox, Point
from src.models.storage.batch import FrameBatch
from src.udfs.abstract_udfs import AbstractClassifierUDF


class R3DVideoClassifier(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "3dresnet"

    def __init__(self, threshold=0.5):
        super().__init__()
        self.threshold = threshold
        self.model = torchvision.models.video.r3d_18(pretrained=args.pre_trained, progress=True)
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            #TODO
        ]

    def _get_predictions(self,video):
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            tensor with labels
        """

        #transform = transforms.Compose([transforms.ToTensor()])

        testset = Cichlids(file_name=video, spatial_transform= spatial_transform)
        testset_loader = DataLoader(testset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

        predictions = self.model(images)


        self.model.eval()  # set model to evaluation mode
        with torch.no_grad():
            for data, target in testset_loader:
                target = target.cuda(async=True)

                data = Variable(data)
                target = Variable(target)

                output = model(data)

        return output

    def classify(self, file_name):
        return self._get_predictions(file_name)


class Cichlids(Dataset):
    """
    A customized data loader for Cichlids.
    """
    def __init__(self,
                 file_name,
                 spatial_transform=None,
                 preload=False):
        """ Intialize the Cichlids dataset

        Args:
            - root: root directory of the dataset
            - tranform: a custom tranform function
            - preload: if preload the dataset into memory
        """
        self.videos = None
        self.labels = None
        self.filename = file_name
        # self.root = root
        self.spatial_transform = spatial_transform

        # read filenames
        # for i, class_dir in enumerate(os.listdir(root)):
        #     filenames = glob.glob(osp.join(root, class_dir, '*.mp4'))
        #     for fn in filenames:
        #         self.filenames.append((fn, i)) # (filename, label) pair

        # if preload dataset into memory
        if preload:
            self._preload()

        # self.len = len(self.filenames)



    def __getitem__(self):
        """ Get a sample from the dataset
        """
        if self.videos is not None:
            # If dataset is preloaded
            video = self.videos[index]
            label = self.labels[index]
        else:
            # If on-demand data loading
            video_fn = self.filename
            video = vp.vread(video_fn)
            video = np.reshape(video, (video.shape[3], video.shape[0], video.shape[1], video.shape[2]))

        if self.spatial_transform is not None:
            self.spatial_transform.randomize_parameters()
            video = video.reshape((video.shape[1], video.shape[2], video.shape[3], video.shape[0]))
            clip = [self.spatial_transform(Image.fromarray(img)) for img in video]
            video = torch.stack(clip, 0).permute(1, 0, 2, 3)

        # return video and label
        return video

    def __len__(self):
        """
        Total number of samples in the dataset
        """
        return self.len


class Compose(object):
    """Composes several transforms together.
    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.
    Example:
        >>> transforms.Compose([
        >>>     transforms.CenterCrop(10),
        >>>     transforms.ToTensor(),
        >>> ])
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for t in self.transforms:
            img = t(img)
        return img

    def randomize_parameters(self):
        for t in self.transforms:
            t.randomize_parameters()


class ToTensor(object):
    """Convert a ``PIL.Image`` or ``numpy.ndarray`` to tensor.
    Converts a PIL.Image or numpy.ndarray (H x W x C) in the range
    [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0].
    """

    def __init__(self, norm_value=255):
        self.norm_value = norm_value

    def __call__(self, pic):
        """
        Args:
            pic (PIL.Image or numpy.ndarray): Image to be converted to tensor.
        Returns:
            Tensor: Converted image.
        """
        if isinstance(pic, np.ndarray):
            # handle numpy array
            img = torch.from_numpy(pic.transpose((2, 0, 1)))
            # backward compatibility
            return img.float().div(self.norm_value)

        if accimage is not None and isinstance(pic, accimage.Image):
            nppic = np.zeros(
                [pic.channels, pic.height, pic.width], dtype=np.float32)
            pic.copyto(nppic)
            return torch.from_numpy(nppic)

        # handle PIL Image
        if pic.mode == 'I':
            img = torch.from_numpy(np.array(pic, np.int32, copy=False))
        elif pic.mode == 'I;16':
            img = torch.from_numpy(np.array(pic, np.int16, copy=False))
        else:
            img = torch.ByteTensor(torch.ByteStorage.from_buffer(pic.tobytes()))
        # PIL image mode: 1, L, P, I, F, RGB, YCbCr, RGBA, CMYK
        if pic.mode == 'YCbCr':
            nchannel = 3
        elif pic.mode == 'I;16':
            nchannel = 1
        else:
            nchannel = len(pic.mode)
        img = img.view(pic.size[1], pic.size[0], nchannel)
        # put it from HWC to CHW format
        # yikes, this transpose takes 80% of the loading time/CPU
        img = img.transpose(0, 1).transpose(0, 2).contiguous()
        if isinstance(img, torch.ByteTensor):
            return img.float().div(self.norm_value)
        else:
            return img

    def randomize_parameters(self):
        pass


class Normalize(object):
    """Normalize an tensor image with mean and standard deviation.
    Given mean: (R, G, B) and std: (R, G, B),
    will normalize each channel of the torch.*Tensor, i.e.
    channel = (channel - mean) / std
    Args:
        mean (sequence): Sequence of means for R, G, B channels respecitvely.
        std (sequence): Sequence of standard deviations for R, G, B channels
            respecitvely.
    """

    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        """
        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be normalized.
        Returns:
            Tensor: Normalized image.
        """
        # TODO: make efficient
        for t, m, s in zip(tensor, self.mean, self.std):
            t.sub_(m).div_(s)
        return tensor

    def randomize_parameters(self):
        pass


class Scale(object):
    """Rescale the input PIL.Image to the given size.
    Args:
        size (sequence or int): Desired output size. If size is a sequence like
            (w, h), output size will be matched to this. If size is an int,
            smaller edge of the image will be matched to this number.
            i.e, if height > width, then image will be rescaled to
            (size * height / width, size)
        interpolation (int, optional): Desired interpolation. Default is
            ``PIL.Image.BILINEAR``
    """

    def __init__(self, size, interpolation=Image.BILINEAR):
        assert isinstance(size,
                          int) or (isinstance(size, collections.Iterable) and
                                   len(size) == 2)
        self.size = size
        self.interpolation = interpolation

    def __call__(self, img):
        """
        Args:
            img (PIL.Image): Image to be scaled.
        Returns:
            PIL.Image: Rescaled image.
        """
        if isinstance(self.size, int):
            w, h = img.size
            if (w <= h and w == self.size) or (h <= w and h == self.size):
                return img
            if w < h:
                ow = self.size
                oh = int(self.size * h / w)
                return img.resize((ow, oh), self.interpolation)
            else:
                oh = self.size
                ow = int(self.size * w / h)
                return img.resize((ow, oh), self.interpolation)
        else:
            return img.resize(self.size, self.interpolation)

    def randomize_parameters(self):
        pass

class RandomHorizontalFlip(object):
    """Horizontally flip the given PIL.Image randomly with a probability of 0.5."""

    def __call__(self, img):
        """
        Args:
            img (PIL.Image): Image to be flipped.
        Returns:
            PIL.Image: Randomly flipped image.
        """
        if self.p < 0.5:
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

    def randomize_parameters(self):
        self.p = random.random()

class MultiScaleRandomCrop(object):

    def __init__(self, scales, size, interpolation=Image.BILINEAR):
        self.scales = scales
        self.size = size
        self.interpolation = interpolation

    def __call__(self, img):
        min_length = min(img.size[0], img.size[1])
        crop_size = int(min_length * self.scale)

        image_width = img.size[0]
        image_height = img.size[1]

        x1 = self.tl_x * (image_width - crop_size)
        y1 = self.tl_y * (image_height - crop_size)
        x2 = x1 + crop_size
        y2 = y1 + crop_size

        img = img.crop((x1, y1, x2, y2))

        return img.resize((self.size, self.size), self.interpolation)

    def randomize_parameters(self):
        self.scale = self.scales[random.randint(0, len(self.scales) - 1)]
        self.tl_x = random.random()
        self.tl_y = random.random()
