from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.udfs.contrib.decorators.ish.io_descriptors.type_exception import TypeException

def setup(input_type: EvaArgument, 
          use_cache: bool,
          input_shape: tuple = None):
    
    def inner_fn(arg_fn):
        def wrapper(*args, **kwargs):
            #custom setup steps for that particular udf
            
            #check type of input
            if not (input_type.check_type(args[0])):
                raise TypeException("Expected %s but received %s" % (input_type.name(), type(args[0])))
            else:
                print("correct input")
                
            #check shape of input
            if input_shape:
                
                if not(input_type.check_shape(args[0], input_shape)):
                    raise TypeException("Mismatch in shape of array.")
                    
            arg_fn(*args, **kwargs)
            
        return wrapper
    
    return inner_fn
