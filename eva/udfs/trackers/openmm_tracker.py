from typing import Tuple
import mmcv
import numpy as np
import pandas as pd
import torch
from mmtrack.models.mot.byte_track import ByteTrack

from eva.udfs.abstract.abstract_udf import AbstractUDF


class OpenMMTracker:
    def __init__(self, config_file: str):
        self.config = mmcv.Config.fromfile(config_file)
        self.model = None

    def track(
        self,
        frame: torch.Tensor,
        bboxes: torch.Tensor,
        labels: torch.Tensor,
        frame_id: int,
    ) -> Tuple:
        """Tracking forward function

        Args:
            frame (torch.Tensor): the input frame with shape (C, H, W)
            bboxes (torch.Tensor): tensor with shape (N, 5)
              in [tl_x, tl_y, br_x, br_y, score]
            labels (torch.Tensor): tensor with shape (N, )
            frame_id (int): the frame id of current frame

        Returns:
            torch.Tensor: tensor with shape (N,)
        """
        track_bboxes, track_labels, ids = self.model.tracker.track(
            img=frame,
            img_metas=None,
            model=self.model,
            bboxes=bboxes,
            labels=labels,
            frame_id=frame_id,
        )
        return track_bboxes, track_labels, ids


class ByteTracker(OpenMMTracker):
    def __init__(self):
        config_file = "/nethome/gkakkar7/VDBMS/eva/eva/udfs/trackers/config/byte.py"
        super().__init__(config_file)
        self.model = ByteTrack(
            tracker=self.config.model["tracker"], motion=self.config.model["motion"]
        )
