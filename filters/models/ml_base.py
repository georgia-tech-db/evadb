"""
This file defines the ml base wrapper class and current ml classes that have been implemented
Feel free to extend the ml models used for filtering by importing contents of this file
If any issues arise, please email jaeho.bang@gmail.com


@Jaeho Bang

"""

from abc import ABCMeta, abstractmethod
import numpy as np



class MLBase(metaclass = ABCMeta):
  def __init__(self):
    # negative numbers indicate they have not been calculated
    # C denotes cost (time it takes to execute)
    # A denotes accuracy (accuracy as in precision - paper shows recalls are of minimum importance)
    # R denotes reduction rate(the images_passed / all_images)
    self.C = -1
    self.A = -1
    self.R = -1
    self.division_rate= 0.8
    self.model = None

  @abstractmethod
  def train(self, X:np.ndarray, y:np.ndarray):
    pass

  @abstractmethod
  def predict(self, X:np.ndarray):
    pass





