import time
import os
import numpy as np
import xml.etree.ElementTree as ET
import pandas as pd
import cv2
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
    self.task_manager = TaskManager.TaskManager()

  @staticmethod
  def image_eval(image_str):
    image_str = ' '.join(image_str.split())
    image_str = image_str.replace(" ", ",")
    image_str = image_str[0] + image_str[2:]
    evaled_image = np.array(eval(image_str))
    height = 540
    width = 960
    channels = 3
    return evaled_image.reshape(height, width, channels)


  @staticmethod
  def load_from_csv(filename):
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_dir = os.path.join(project_dir, "data", "pandas", filename)
    converters = {"image": Load().image_eval, "vehicle_type": eval, "color": eval, "intersection": eval}
    panda_file = pd.read_csv(full_dir, converters=converters)
    for key in panda_file:
      if "Unnamed" in key:
        continue


    return panda_file


  @staticmethod
  def save(filename, panda_data):
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #Eva / eva
    csv_folder = os.path.join(project_dir, "data", "pandas")
    if os.path.exists(csv_folder) == False:
      os.makedirs(csv_folder)
    csv_filename = os.path.join(csv_folder, filename)
    panda_data.to_csv(csv_filename, sep=",", index = None)

  def load(self, dir_dict):
    # we can extract speed, vehicle_type from the XML
    # we need to extract color, intersection from code
    train_image_dir = dir_dict['train_image']
    test_image_dir = dir_dict['test_image']
    train_anno_dir = dir_dict['train_anno']
    labels_list = ["vehicle_type", "color", "speed", "intersection"]

    if __debug__: print("Inside load, starting image loading...")
    train_img_array = self._load_images(train_image_dir)
    if __debug__: print("Done loading train images.. shape of matrix is " + str(train_img_array.shape))

    vehicle_type_labels, speed_labels, color_labels, intersection_labels = self._load_XML(train_anno_dir, train_img_array)
    if __debug__: print("Done loading the labels.. length of labels is " + str(len(vehicle_type_labels)))

    #n_samples, height, width, channels = train_img_array.shape
    #train_img_array = train_img_array.reshape(n_samples, height*width*channels)

    if __debug__: print("train img array flatten is ", str(train_img_array.shape))
    data_table = list(zip(vehicle_type_labels, color_labels, speed_labels, intersection_labels))

    if __debug__: print("data_table shape is ", str(len(data_table)))

    columns = labels_list
    dt_train = pd.DataFrame(data = data_table, columns = columns)
    if __debug__: print("Done making panda table for train")

    dt_test = None
    if test_image_dir is not None:
      test_img_list = self._load_images(test_image_dir)
      if __debug__: print("Done loading test images.. shape of matrix is " + str(test_img_list.shape))

      dt_test = pd.DataFrame(data = list(test_img_list), columns = ['image'])
      if __debug__: print("Done making panda table for test")
    return [train_img_array, dt_train, dt_test]


  def _convert_speed(self, original_speed):
    """
    TODO: Need to actually not use this function, because we need to find out what the original speed values mean
    TODO: However, in the meantime, we will use this extrapolation....
    :param original_speed:
    :return: converted_speed
    """
    speed_range = [0.0, 20.0]
    converted_range = [0.0, 100.0]

    return original_speed * 5


  def _load_XML(self, directory, images):
    car_labels = []
    speed_labels = []
    color_labels = []
    intersection_labels = []

    for root, subdirs, files in os.walk(directory):
      files.sort()
      for file in files:
        file_path = os.path.join(root, file)
        if ".swp" in file_path:
          continue
        tree = ET.parse(file_path)
        tree_root = tree.getroot()
        start_frame_num = 1
        start_frame = True
        for frame in tree_root.iter('frame'):
          curr_frame_num = int(frame.attrib['num'])
          if start_frame and curr_frame_num != start_frame_num:
            car_labels.append( [None] * (curr_frame_num - start_frame_num) )
            speed_labels.append( [None] * (curr_frame_num - start_frame_num) )


          car_per_frame = []
          speed_per_frame = []
          color_per_frame = []
          intersection_per_frame = []

          bboxes = []
          for box in frame.iter('box'):
            left = int(eval(box.attrib['left']))
            top = int(eval(box.attrib['top']))
            right = left + int(eval(box.attrib['width']))
            bottom = top + int(eval(box.attrib['height']))
            bboxes.append([left, top, right, bottom])
          # curr_frame_num -1 comes from the fact that indexes start from 0 whereas the start_frame_num = 1
          color_per_frame = self.task_manager.call_color(images[curr_frame_num - 1], bboxes)
          #if __debug__: print("colors detected in this frame are " , str(color_per_frame))
          scene = file.replace(".xml", "") #MVI_20011.xml -> MVI_20011
          intersection_per_frame = self.task_manager.call_intersection(images[curr_frame_num - 1], scene, bboxes)


          for att in frame.iter('attribute'):
            if (att.attrib['vehicle_type']):
              car_per_frame.append(att.attrib['vehicle_type'])
            if (att.attrib['speed']):
              speed_per_frame.append( self._convert_speed(float(att.attrib['speed'])) )
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

          start_frame = False

    return [car_labels, speed_labels, color_labels, intersection_labels]





  def _load_images(self, image_dir, downsize_rate = 1, grayscale = False):
    file_names = []
    for root, subdirs, files in os.walk(image_dir):
      files.sort()
      for file in files:
        file_names.append(os.path.join(root, file))

    if grayscale == False:
      img_table = np.ndarray(shape=(len(file_names), self.image_height / downsize_rate, self.image_width / downsize_rate, self.image_channels), dtype=np.int16)
    else:
      img_table = np.ndarray(shape=(len(file_names), self.image_height / downsize_rate, self.image_width / downsize_rate, 1), dtype=np.int16)

    for i in xrange(len(file_names)):
      file_name = file_names[i]
      if grayscale:
        img = load_img(file_name, color_mode = "grayscale",
                       target_size = (self.image_height / downsize_rate, self.image_width / downsize_rate))
      else:
        img = load_img(file_name,
                       target_size=(self.image_height / downsize_rate, self.image_width / downsize_rate))

      img_table[i] = img_to_array(img)

    return img_table


  def load_images_nn(self, image_dir, downsize_rate = 1, grayscale = False):
    """
    Loading images in a non normalized form
    :param image_dir:
    :param downsize_rate:
    :param grayscale:
    :return:
    """
    file_names = []
    for root, subdirs, files in os.walk(image_dir):
      files.sort()
      for file in files:
        file_names.append(os.path.join(root, file))

    if grayscale == False:
      img_table = np.ndarray(shape=(len(file_names), self.image_height / downsize_rate, self.image_width / downsize_rate, self.image_channels), dtype=np.int16)
    else:
      img_table = np.ndarray(shape=(len(file_names), self.image_height / downsize_rate, self.image_width / downsize_rate, 1), dtype=np.int16)

    for i in xrange(len(file_names)):
      file_name = file_names[i]
      if grayscale:
        img = cv2.imread(file_name,0)
      else:
        img = cv2.imread(file_name, 1)

      img = cv2.resize(img, (self.image_width / downsize_rate, self.image_height / downsize_rate))
      img_table[i] = img[:,:, np.newaxis]



    return img_table






class LoadTest:
  def __init__(self, load):
    self.load = load



  def run(self):
    start_time = time.time()
    eva_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "small-data")
    #test_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "test_images")
    test_image_dir = None
    train_anno_dir = os.path.join(eva_dir, "data", "ua_detrac", "small-annotation")
    dir_dict = {"train_image": train_image_dir,
                "test_image": test_image_dir,
                "train_anno": train_anno_dir}

    if __debug__:
      print("train image dir: " + train_image_dir)
      #print("test image dir: " + test_image_dir)
      print("train annotation dir: " + train_anno_dir)

    dt_train, dt_test = self.load.load(dir_dict)
    Load().save("small.csv", dt_train)

    if __debug__:
      print("--- Total Execution Time : %.3f seconds ---" % (time.time() - start_time))

      print(dt_train.shape)
      if test_image_dir != None: print(dt_test.shape)


if __name__ == "__main__":
    load = Load()
    load_test = LoadTest(load)
    #load_test.run()
    panda_table = Load().load_from_csv("small.csv")
    a = 1 + 2
    if __debug__: print("panda shape is " + str(panda_table.shape))
