from inspect import FrameInfo
import os
import pickle
import subprocess
import torch
from eva.configuration.constants import EVA_DEFAULT_DIR
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from eva.utils.logging_manager import logger
import numpy as np
from torchvision.transforms import Normalize
from torchvision import transforms
import pandas as pd
import cv2
import torch
import pickle
from eva.utils.logging_manager import logger
from torch import nn


class TimeDistributed(torch.nn.Module):
    # base model borrowed from Zamba pretrained model:
    # https://github.com/drivendataorg/zamba/blob/master/zamba/pytorch/layers.py
    """Applies `module` over `tdim` identically for each step, use `low_mem` to compute one at a time.

    NOTE: vendored (with minor adaptations) from fastai:
    https://github.com/fastai/fastai/blob/4b0785254fdece1a44859956b6e54eedb167a97e/fastai/layers.py#L510-L544

    Updates:
     - super.__init__() in init
     - assign attributes in init
     - inherit from torch.nn.Module rather than fastai.Module
    """
    def _stack_tups(tuples, stack_dim=1):
        """Stack tuple of tensors along `stack_dim`

        NOTE: vendored (with minor adaptations) from fastai:
        https://github.com/fastai/fastai/blob/4b0785254fdece1a44859956b6e54eedb167a97e/fastai/layers.py#L505-L507

        Updates:
            -  use `range` rather than fastai `range_of`
        """
        return tuple(torch.stack([t[i] for t in tuples], dim=stack_dim) for i in range(len(tuples[0])))

    def __init__(self, module, low_mem=False, tdim=1):
        super().__init__()
        self.low_mem = low_mem
        self.tdim = tdim
        self.module = module

    def forward(self, *tensors, **kwargs):
        "input x with shape:(bs,seq_len,channels,width,height)"
        if self.low_mem or self.tdim != 1:
            return self.low_mem_forward(*tensors, **kwargs)
        else:
            # only support tdim=1
            inp_shape = tensors[0].shape
            bs, seq_len = inp_shape[0], inp_shape[1]
            out = self.module(*[x.view(bs * seq_len, *x.shape[2:]) for x in tensors], **kwargs)
        return self.format_output(out, bs, seq_len)

    def low_mem_forward(self, *tensors, **kwargs):
        "input x with shape:(bs,seq_len,channels,width,height)"
        seq_len = tensors[0].shape[self.tdim]
        args_split = [torch.unbind(x, dim=self.tdim) for x in tensors]
        out = []
        for i in range(seq_len):
            out.append(self.module(*[args[i] for args in args_split]), **kwargs)
        if isinstance(out[0], tuple):
            return TimeDistributed._stack_tups(out, stack_dim=self.tdim)
        return torch.stack(out, dim=self.tdim)

    def format_output(self, out, bs, seq_len):
        "unstack from batchsize outputs"
        if isinstance(out, tuple):
            return tuple(out_i.view(bs, seq_len, *out_i.shape[1:]) for out_i in out)
        return out.view(bs, seq_len, *out.shape[1:])

    def __repr__(self):
        return f"TimeDistributed({self.module})"
class AnimalDetector(PytorchAbstractClassifierUDF):
    @property
    def name(self) -> str:
        return "AnimalDetector"
    
    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> 'List[str]':
        return ['blank', 'non_blank']


    def setup(self, threshold=0.85):
        self.threshold = threshold
        # pull the necessary checkpoints and model architectures
        output_directory = os.path.join(EVA_DEFAULT_DIR, "udfs", "models")
        subprocess.run(["mkdir", "-p", output_directory])
        base_module_arc_path = os.path.join(output_directory, "base_module_arc_blank")
        base_module_ckt_path = os.path.join(output_directory, "base_module_blank.pt")
        classifier_ckt_path = os.path.join(output_directory, "classifier_blank.pt")
        file_urls = [
            "https://www.dropbox.com/s/rsu3ig9d168mj05/base_module_arc_blank?dl=0",
            "https://www.dropbox.com/s/eejcvyzh1ama24r/base_module_blank.pt?dl=0",
            "https://www.dropbox.com/s/ltsnv527fwk481r/classifier_blank.pt?dl=0",
        ]
        file_paths = [
            base_module_arc_path,
            base_module_ckt_path,
            classifier_ckt_path,
        ]
        # pull model from dropbox if not present
        for i in range(len(file_urls)):
            if not os.path.exists(file_paths[i]):
                subprocess.run(["wget", file_urls[i], "--output-document", file_paths[i]])

        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # init self.base
        module = None
        with open(base_module_arc_path,"rb") as f:
            module = pickle.load(f)
        module.load_state_dict(torch.load(base_module_ckt_path, map_location=device))
        self.base = TimeDistributed(module)

        # init self.classifier
        self.classifier = torch.nn.Sequential(
            nn.Linear(2152, 256),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.Flatten(),
            nn.Linear(1024, 1),

        )
        self.classifier.load_state_dict(torch.load(classifier_ckt_path, map_location=device))

    def ensure_frame_number(arr, total_frames: int):
        # preprocess borrowed from Zamba pretrained model
        # https://github.com/drivendataorg/zamba/blob/master/zamba/data/video.py
        if (total_frames is None) or (arr.shape[0] == total_frames):
            return arr
        elif arr.shape[0] == 0:
            logger.warning(
                "No frames selected. Returning an array in the desired shape with all zeros."
            )
            return np.zeros((total_frames, arr.shape[1], arr.shape[2], arr.shape[3]), dtype="int")
        elif arr.shape[0] > total_frames:
            logger.info(
                f"Clipping {arr.shape[0] - total_frames} frames "
                f"(original: {arr.shape[0]}, requested: {total_frames})."
            )
            return arr[:total_frames]
        elif arr.shape[0] < total_frames:
            logger.info(
                f"Duplicating last frame {total_frames - arr.shape[0]} times "
                f"(original: {arr.shape[0]}, requested: {total_frames})."
            )
            return np.concatenate(
                [arr, np.tile(arr[-1], (total_frames - arr.shape[0], 1, 1, 1))], axis=0
            )

    def image_model_transforms():  
        # preprocess borrowed from zamba pretained model
        # https://github.com/drivendataorg/zamba/blob/master/zamba/pytorch/transforms.py
        class ConvertTHWCtoTCHW(torch.nn.Module):
            """Convert tensor from (T, H, W, C) to (T, C, H, W)"""

            def forward(self, vid: torch.Tensor) -> torch.Tensor:
                return vid.permute(0, 3, 1, 2)
        class Uint8ToFloat(torch.nn.Module):
            def forward(self, tensor: torch.Tensor) -> torch.Tensor:
                return tensor / 255.0
        
        imagenet_normalization_values = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        img_transforms = [
            ConvertTHWCtoTCHW(),
            Uint8ToFloat(),
            Normalize(**imagenet_normalization_values),
        ]

        return transforms.Compose(img_transforms)
    
    def transform_video(frames)->'Tensor':
        if len(frames.shape) < 4:
            frames = frames.unsqueeze(0)
        # split the tensor to multiple images and do the following transforms one by one
        arr_list = []
        for i in range(frames.shape[0]):
            frame = frames[i]
            to_img = transforms.ToPILImage()
            img = to_img(frame)
            np_img = np.asarray(img)
            arr_list.append(np_img)
        arr = np.array(arr_list)
        # preprocess borrowed from zamba
        # https://github.com/drivendataorg/zamba/blob/master/zamba/data/video.py
        model_input_height, model_input_width = 240, 426
        if (model_input_height is not None) and (model_input_width is not None):
            resized_frames = np.zeros(
                (arr.shape[0], model_input_height, model_input_width, 3), np.uint8
            )
            for ix, f in enumerate(arr):
                if (f.shape[0] != model_input_height) or (
                    f.shape[1] != model_input_width
                ):
                    f = cv2.resize(
                        f,
                        (model_input_width, model_input_height),
                        # https://stackoverflow.com/a/51042104/1692709
                        interpolation=(
                            cv2.INTER_LINEAR
                            if f.shape[1] < model_input_width
                            else cv2.INTER_AREA
                        ),
                    )
                resized_frames[ix, ...] = f
            arr = np.array(resized_frames)
        arr = AnimalDetector.ensure_frame_number(arr, 16)
        return torch.Tensor(arr)

    def forward(self, frames):
        torch.set_grad_enabled(False)
        frames = AnimalDetector.transform_video(frames)
        transform = AnimalDetector.image_model_transforms()
        frames = transform(frames)
        frames = frames.unsqueeze(0)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        to_base = frames.to(device)
        to_classifier = self.base(to_base)
        y_hat = self.classifier(to_classifier)
        pred = torch.sigmoid(y_hat).cpu().numpy()
        outcome = pd.DataFrame()
        for frame_output in pred:
            blank_score = frame_output[0]
            if blank_score > self.threshold:
                outcome = outcome.append({'labels': ['blank'], 'scores': [blank_score]}, ignore_index=True,)
            else:
                outcome = outcome.append({'labels': ['non_blank'], 'scores': [1 - blank_score]}, ignore_index=True,)
        return outcome

        
class AnimalDetectorPlus(AnimalDetector):
    @property
    def labels(self) -> 'List[str]':
        return ['aardvark',
            'antelope_duiker',
            'badger',
            'bat',
            'bird',
            'blank',
            'cattle',
            'cheetah',
            'chimpanzee_bonobo',
            'civet_genet',
            'elephant',
            'equid',
            'forest_buffalo',
            'fox',
            'giraffe',
            'gorilla',
            'hare_rabbit',
            'hippopotamus',
            'hog',
            'human',
            'hyena',
            'large_flightless_bird',
            'leopard',
            'lion',
            'mongoose',
            'monkey_prosimian',
            'pangolin',
            'porcupine',
            'reptile',
            'rodent',
            'small_cat',
            'wild_dog_jackal']

    def setup(self, threshold= 0.5):
        self.threshold = threshold
        # pull the necessary checkpoints and model architectures
        output_directory = os.path.join(EVA_DEFAULT_DIR, "udfs", "models")
        subprocess.run(["mkdir", "-p", output_directory])
        base_module_arc_path = os.path.join(output_directory, "base_module_arc_timedistributed")
        base_module_ckt_path = os.path.join(output_directory, "base_module_timedistributed.pt")
        classifier_ckt_path = os.path.join(output_directory, "classifier_timedistributed.pt")
        file_urls = [
            "https://www.dropbox.com/s/uh9qx9afvsklcy8/base_module_arc_timedistributed?dl=0",
            "https://www.dropbox.com/s/sndqlvg59kkq0tq/base_module_timedistributed.pt?dl=0",
            "https://www.dropbox.com/s/kiet243u2jocacc/classifier_timedistributed.pt?dl=0",
        ]
        file_paths = [
            base_module_arc_path,
            base_module_ckt_path,
            classifier_ckt_path,
        ]
        # pull model from dropbox if not present
        for i in range(len(file_urls)):
            if not os.path.exists(file_paths[i]):
                subprocess.run(["wget", file_urls[i], "--output-document", file_paths[i]])

        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # init self.base
        module = None
        with open(base_module_arc_path,"rb") as f:
            module = pickle.load(f)
        module.load_state_dict(torch.load(base_module_ckt_path, map_location=device))
        self.base = TimeDistributed(module)

        # init self.classifier
        self.classifier = torch.nn.Sequential(
            nn.Linear(2152, 256),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.Flatten(),
            nn.Linear(1024, 32),

        )
        self.classifier.load_state_dict(torch.load(classifier_ckt_path, map_location=device))
    
    def forward(self, frames):
        torch.set_grad_enabled(False)
        frames = AnimalDetector.transform_video(frames)
        transform = AnimalDetector.image_model_transforms()
        frames = transform(frames)
        frames = frames.unsqueeze(0)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        to_base = frames.to(device)
        to_classifier = self.base(to_base)
        y_hat = self.classifier(to_classifier)
        pred = torch.sigmoid(y_hat).cpu().numpy()
        outcome = pd.DataFrame()
        def filter_by_threshold(series: 'pd.Series'):
            assert len(series.labels) == len(series.scores)
            new_labels = []
            new_scores = []
            for i in range(len(series.labels)):
                if series.scores[i] >= self.threshold:
                    new_labels.append(series.labels[i])
                    new_scores.append(series.scores[i])
            series.labels = new_labels
            series.scores = new_scores
                    
        for frame_output in pred:
            outcome = outcome.append({'labels': self.labels, 'scores': frame_output}, ignore_index=True,)
            filter_by_threshold(outcome.iloc[-1])
        return outcome