import sys

#functools.singledispatchmethod is supported only in python versions >=3.8
if sys.version_info >= (3, 8):
    from functools import singledispatchmethod
else:
    # https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
    from functools import singledispatch, update_wrapper

    def singledispatchmethod(func):
        """
        This is done to support overloading functions via single dispatch. 
        With single dispatch we can define multiple implementations of a function 
        and have it chosen based on a single argument.

        @singledispatch 
        def my_func(arg1):
            print("default ", arg1)

        @myfunc.register(str)
        def my_func(arg1):
            print("string implementation: ", arg1)
        
        @myfunc.register(int)
        def my_func(arg1):
            print("integer implementation: ", arg1)

        When we call my_func with a string argument the string implementation is called
        and we when we call my_func with integer argument, the integer implementation is 
        called. 
        """
        dispatcher = singledispatch(func)

        def wrapper(*args, **kw):
            return dispatcher.dispatch(args[1].__class__)(*args, **kw)

        wrapper.register = dispatcher.register
        update_wrapper(wrapper, func)
        return wrapper


