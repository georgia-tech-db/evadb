from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.udfs.contrib.decorators.ish.io_descriptors.type_exception import TypeException
import torch
import yolov5
from typing import List
import pandas as pd



def setup(use_cache: bool,
          udf_type: str,
          batch: bool,
          model_path: str = None
          ):
    
    def inner_fn(arg_fn):
        print("Cache is set: ", use_cache)
        print("batching is set: ", batch)
        
        def wrapper(*args, **kwargs):
            
            #setup the model
            if udf_type == "object_detection":
                if model_path:
                    args[0].model = torch.load(model_path)
                else:
                    args[0].model = yolov5.load("yolov5s.pt", verbose=False)
                    
            #set the batch and caching parameters.
            
            arg_fn(*args, **kwargs)
            
        return wrapper
    
    return inner_fn


def forward(input_signature: EvaArgument): 
    
    def inner_fn(arg_fn):
       
        def wrapper(*args):
            
            frames = args[1]
        
            #check type of input
            if not (input_signature.check_type(frames)):
                raise TypeException("Expected %s but received %s" % (input_signature.name(), type(args[0])))
            else:
                print("correct input")
                
            #check shape of input
            if input_signature:
                if not(input_signature.check_shape(frames)):
                    raise TypeException("Mismatch in shape of array.")

            #first argument is self and second is frames.
            output =  arg_fn(args[0], frames)
            
            return output
        
        return wrapper
    
    return inner_fn

