import time
import os
import numpy as np
import xml.etree.ElementTree as ET
import pandas as pd
from keras.preprocessing.image import img_to_array, load_img

import TaskManager

#Make this return a dictionary of label to data for the whole dataset

class Load:
  def __init__(self, image_width = 960, image_height = 540):
    self.data_dict = {}
    self.label_dict = {}
    self.vehicle_type_filters = ['car', 'van', 'bus', 'others']
    self.speed_filters = [40, 50, 60, 65, 70]
    self.intersection_filters = ["pt335", "pt342", "pt211", "pt208"]
    self.color_filters = ['white', 'black', 'silver', 'red']
    self.image_width = image_width
    self.image_height = image_height
    self.image_channels = 3
    self.task_manager = TaskManager.TaskManager


  def load(self, dir_dict):
    # we can extract speed, vehicle_type from the XML
    # we need to extract color, intersection from code
    train_image_dir = dir_dict['train_image']
    test_image_dir = dir_dict['test_image']
    train_anno_dir = dir_dict['train_anno']
    labels_list = ["vehicle_type", "color", "speed", "intersection"]

    train_img_list = self._load_images(train_image_dir)
    test_img_list = self._load_images(test_image_dir)

    vehicle_type_labels, speed_labels, color_labels, intersection_labels = self._load_XML(train_anno_dir, train_img_list)


    data_table = list(zip(train_img_list, vehicle_type_labels, color_labels, speed_labels, intersection_labels))

    columns = ["image"] + labels_list
    dt_train = pd.DataFrame(data = data_table, columns = columns)
    dt_test = pd.DataFrame(data = list(test_img_list), columns = ['image'])
    return [dt_train, dt_test]



  def _load_XML(self, directory, images):
    car_labels = []
    speed_labels = []
    color_labels = []
    intersection_labels = []

    for root, subdirs, files in os.walk(directory):
      files.sort()
      for file in files:
        file_path = os.path.join(root, file)
        tree = ET.parse(file_path)
        tree_root = tree.getroot()
        start_frame_num = 1
        for frame in tree_root.iter('frame'):
          curr_frame_num = int(frame.attrib['num'])
          if (curr_frame_num != start_frame_num):
            car_labels.append( [None] * (curr_frame_num - start_frame_num) )
            speed_labels.append( [None] * (curr_frame_num - start_frame_num) )
          start_frame_num = curr_frame_num

          car_per_frame = []
          speed_per_frame = []
          color_per_frame = []
          intersection_per_frame = []

          bboxes = []
          for box in frame.iter('box'):
            left = float(box.attrib['left'])
            top = float(box.attrib['top'])
            right = left + float(box.attrib['width'])
            bottom = top + float(box.attrib['height'])
            bboxes.append([left, top, right, bottom])
          color_per_frame = self.task_manager.call_color(images[curr_frame_num], bboxes)
          intersection_per_frame = self.task_manager.call_intersection(images[curr_frame_num])


          for att in frame.iter('attribute'):
            if (att.attrib['vehicle_type']):
              car_per_frame.append(att.attrib['vehicle_type'])
            if (att.attrib['speed']):
              speed_per_frame.append(float(att.attrib['speed']))
          assert(len(car_per_frame) == len(speed_per_frame))
          assert(len(car_per_frame) == len(color_per_frame))
          assert(len(car_per_frame) == len(intersection_per_frame))

          if len(car_per_frame) == 0:
            car_labels.append(None)
          else:
            car_labels.append(car_per_frame)

          if len(speed_per_frame) == 0:
            speed_labels.append(None)
          else:
            speed_labels.append(speed_per_frame)

          if len(color_per_frame) == 0:
            color_labels.append(None)
          else:
            color_labels.append(color_per_frame)

          if len(intersection_per_frame) == 0:
            intersection_labels.append(None)
          else:
            intersection_labels.append(intersection_per_frame)

    return [car_labels, speed_labels, color_labels, intersection_labels]





  def _load_images(self, image_dir):
    file_names = []
    for root, subdirs, files in os.walk(image_dir):
      files.sort()
      for file in files:
        file_names.append(os.path.join(root, file))

    img_table = np.ndarray(shape=(len(file_names), self.image_height, self.image_width, self.image_channels), dtype=np.int16)


    for i in xrange(len(file_names)):
      file_name = file_names[i]
      img = load_img(file_name, target_size = (self.image_height, self.image_width))
      img_table[i] = img_to_array(img)

    return img_table








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

