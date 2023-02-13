
import numpy as np
import pandas as pd
import torch
from facenet_pytorch import MTCNN
import yolov5
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF


def setup(model_type, device_type, threshold= 0.5, model_path=None):
    
    def inner_fn(arg_fn):
        
        def wrapper(*args, **kwargs):
            #custom setup steps for that particular udf
            if model_type == "face_detection":
                args[0].model = MTCNN(torch.device(device_type))
            elif model_type == "object_dectection_yolo":
                if not model_path:
                    args[0].model = yolov5.load("yolov5s.pt", verbose=False)
                else:
                    args[0].model = yolov5.load(model_path)
                    
            arg_fn(*args, **kwargs)
            
        return wrapper
    
    return inner_fn
    
    
def forward():
    
    def inner_fn(arg_fn):
        
        def wrapper(*args):
            
            frames_arr = args[1]
            
            frames_arr = torch.permute(frames_arr, (0, 2, 3, 1))
            
            args[0].predictions = args[0].model([its.cpu().detach().numpy() * 255 for its in frames_arr])
            
            outcome = arg_fn(args[0], frames_arr)
            
            return pd.DataFrame(
                outcome,
                columns=[
                    "labels",
                    "bboxes",
                    "scores",
                ],
            )
        
        return wrapper
    
    return inner_fn

