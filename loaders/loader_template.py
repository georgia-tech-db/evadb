"""
This file defines the interface all dataset loaders need to follow / implement
If any issues arise, please email jaeho.bang@gmail.com

@Jaeho Bang
"""
from abc import ABCMeta, abstractmethod
import numpy as np

class LoaderTemplate(metaclass=ABCMeta):


  @abstractmethod
  def load_images(self, dir:str):
    pass

  @abstractmethod
  def load_labels(self, dir:str):
    pass

  @abstractmethod
  def load_boxes(self, dir:str):
    pass

  @abstractmethod
  def load_video(self, dir:str):
    pass




