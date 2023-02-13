from eva.udfs.new_udf_impl.base_udf_fns import setup, forward


import pandas as pd
import numpy as np
from typing import List

from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
import cv2


try:
    import torch
    from torch import Tensor

except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )


class YoloDecorators(PytorchAbstractClassifierUDF):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @property
    def name(self) -> str:
        return "yolo"
    
    property
    def labels(self) -> List[str]:
        pass
    
    @setup(
        model_type="object_dectection_yolo", 
        threshold=0.85,
        device_type="GPU"
    )
    def setup(self):
        pass
    

    @forward()    
    def forward(self, frames_arr) :
        outcome = []
        for i in range(frames_arr.shape[0]):
            single_result = self.predictions.pandas().xyxy[i]
            
            pred_class = single_result["name"].tolist()
            pred_score = single_result["confidence"].tolist()
            pred_boxes = single_result[["xmin", "ymin", "xmax", "ymax"]].apply(
                lambda x: list(x), axis=1
            )

            outcome.append(
                {
                    "labels": pred_class,
                    "bboxes": pred_boxes,
                    "scores": pred_score,
                }
            )
        
        return pd.DataFrame(
            outcome,
            columns=[
                "labels",
                "bboxes",
                "scores",
            ],
        )
        
        
   
