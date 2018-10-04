import time
import os
import numpy as np
import xml.etree.ElementTree as ET
from keras.preprocessing.image import img_to_array, load_img

#Make this return a dictionary of label to data for the whole dataset

class Load:
  def __init__(self, name="ua_detrac"):
    self.data_dict = {}
    self.label_dict = {}
		#TODO: Make this inheritance
    prefix = "data/"
    if name == "ua_detrac":
      self.label_path = prefix + name + '/small-annotation/'
      self.input_path = prefix + name + '/small-data/'
      self.vehtype_filters = ['car', 'van', 'bus', 'others']
      self.weather_filters = ['cloudy', 'night', 'sunny', 'rainy']
      self.vehcolor_filters = ['white', 'black', 'silver', 'red']
      #TODO: There are 2 more types of filters mentioned in the paper: i(where it starts), o(where it ends)
      if __debug__:
        print(self.label_path)
        print(self.input_path)

    else:
      raise Exception

  def load_dataset(self):
    list_of_files = []
    num_frames_list = []
    for root, subdirs, files in os.walk(self.input_path):
      subdirs.sort()
      for dire in subdirs:
        listd = os.listdir(os.path.join(root, dire))
        num_frames_list.append(len(listd))
      for filename in sorted(files):
        file_path = os.path.join(root, filename)
        list_of_files.append(file_path)
    if __debug__:
      print "Number of files: " + str( len(list_of_files) )
    image_width = 960
    image_height = 540
    ratio = 12
    image_width = int(image_width / ratio)
    image_height = int(image_height / ratio)
    channels = 3
    X = np.ndarray(shape=(len(list_of_files), image_height, image_width, channels), dtype=np.float32)
    i = 0
    for file in list_of_files:
      img = load_img(file, target_size=(image_height, image_width))
      X[i] = img_to_array(img)
      X[i] = (X[i] - 128) / 128
      i += 1

    nsamples, nx, ny, nc = X.shape
    #X = X.reshape((nsamples, nx * ny * nc))
    if __debug__: print ("Loaded %d inputs" % nsamples)
    for item in self.vehtype_filters:
      y = self.get_vehtype_labels(item, num_frames_list)
      y = np.array(y)
      self.label_dict[item] = y #label will be in the format of 0,1s

    return X, self.label_dict

  def get_vehtype_labels(self, filter, num_frames_list):
    y = []
    for root, subdirs, files in os.walk(self.label_path):
      i = 0
      for filename in sorted(files):
        file_path = os.path.join(root, filename)
        tree = ET.parse(file_path)
        tree_root = tree.getroot()
        j = 1
        for frame in tree_root.iter('frame'):
          if (int(frame.attrib['num']) != j):
            for t in range(0, int(frame.attrib['num']) - j):
              y.append(0)
            j = int(frame.attrib['num'])
          flag = 0
          for attribute in frame.iter('attribute'):
            if (attribute.attrib['vehicle_type'] == filter):
              y.append(1)
              flag = 1
              break
          if (flag == 0):
            y.append(0)
          j += 1
        if (j != num_frames_list[i]):
          for t in range(0, num_frames_list[i] - j + 1):
            y.append(0)
          j = num_frames_list[i]
        i += 1
    return y


class LoadTest:
  def __init__(self, load):
    self.load = load

  def run(self):
    start_time = time.time()
    self.load.load_dataset()
    if __debug__: print("--- Total Execution Time : %.3f seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    load = Load()
    load_test = LoadTest(load)
    load_test.run()

