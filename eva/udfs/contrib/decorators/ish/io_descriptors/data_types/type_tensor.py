from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
import numpy as np
import torch

class PyTorchTensor(EvaArgument):
    
    def __init__(self, shape = None, dtype = None) -> None:
        super().__init__()
        self.shape = shape
        self.dtype = dtype
        
    def check_type(self, input_object) -> bool:
        if self.dtype:
            if self.dtype == "int32":
                return (isinstance(input_object, torch.Tensor) and (input_object.dtype == torch.int32))
            elif self.dtype == "float16":
                return (isinstance(input_object, torch.Tensor) and (input_object.dtype == torch.float16))
            elif self.dtype == "float32":
                return (isinstance(input_object, torch.Tensor) and (input_object.dtype == torch.float32))
            
        else:
            return isinstance(input_object, torch.Tensor)

    
    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False
            
        return True
            
    def name(self):
        return "PyTorch Tensor"
        
        


    