from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
import numpy as np

class NumpyArray(EvaArgument):
    
    def __init__(self) -> None:
        super().__init__()
        
        
    def check_type(self, input_object) -> bool:
        return isinstance(input_object, np.ndarray)
    
    def check_shape(self, input_object, required_shape) -> bool:
        print(input_object.shape)
        print(required_shape)
        if input_object.shape != required_shape:
            return False
        
        return True
            
    
    def name(self):
        return "NumpyArray"
        
        


    