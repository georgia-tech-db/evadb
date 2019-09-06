"""
This file defines the interface all dataset loaders need to follow / implement
If any issues arise, please email jaeho.bang@gmail.com

@Jaeho Bang
"""
from abc import ABCMeta, abstractmethod
import numpy as np

class LoaderBase(metaclass=ABCMeta):


  @abstractmethod
  def load_images(self):
    pass

  @abstractmethod
  def load_labels(self):
    pass

  @abstractmethod
  def load_boxes(self):
    pass

  @abstractmethod
  def load_video(self):
    pass




