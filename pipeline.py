
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import cv2
import os
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import img_to_array, load_img, array_to_img, save_img


import filters.load as load
import filters.pp as pp
import query_optimizer.query_optimizer as qo


#TODO: Fill this file in with the components loaded from other files
class Pipeline:
  """1. Load the dataset
     2. Load the QO
     3. Load the Filters
     4. Load the Central Network (RFCNN, SVM for other labels etc)
     5. Listen to Queries
     6. Give back result"""

  def __init__(self):
    self.load = load.Load()
    self.pp = pp.PP()
    #self.qo = qo.QueryOptimizer()

  # We have access to train and test dataset -> Used for finding the score and evaluation
  def filter_performance_test(self):
    start_time = time.time()

    data, label_dict = self.load.load_dataset()
    nsamples, nx, ny, nc = data.shape
    data = data.reshape((nsamples, nx * ny * nc))

    #TODO: Split the dataset into train, val, test (val should be used for evaluating the pps
    #TODO: (continued) -> Need to look at paper to make sure it is the correct way
    X = pd.DataFrame(data)
    for label in label_dict:
      y = pd.Series(label_dict[label])
      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42)
      break

    train_index = X_train.index.values
    test_index = X_test.index.values
    label_dict_train = {}
    label_dict_test = {}
    for label in label_dict:
      label_dict_train[label] = label_dict[label][train_index]
      label_dict_test[label] = label_dict[label][test_index]


    print("--- Total Execution Time for loading the dataset: %.3f seconds ---" % (time.time() - start_time))

    start_time = time.time()
    self.pp.train_all(X_train, label_dict_train)
    print("--- Total Execution Time for training the dataset : %.3f seconds ---" % (time.time() - start_time))
    if __debug__:
      print X_train.shape
      print X_test.shape

    category_stats = self.pp.evaluate(X_test, label_dict_test)
    print category_stats

    xs = self.pp.predict(X_test[0:100], "car", "none/dnn", bool=False)
    xs = xs.values
    nsamples = xs.shape[0]
    xs_reshaped = xs.reshape((nsamples, nx, ny, nc))
    description_str = "label: " + "car\n" + "model: none/dnn\n"
    self.save_image(xs_reshaped, description_str)

    print "finished saving images..."
    return

  def save_image(self, xs, description):
    project_path = os.path.dirname(os.path.abspath(__file__))
    count = 100
    for x in xs:
      img1 = array_to_img(x)
      save_img(path=os.path.join(project_path, 'examples', str(count) + '.jpg'), x=img1, file_format='jpeg')
      count += 1
    return

  # Actual run of the pipeline
  def run(self):
    start_time = time.time()

    data, label_dict = self.load.load_dataset()
    print("--- Total Execution Time for loading the dataset: %.3f seconds ---" % (time.time() - start_time))

    start_time = time.time()
    self.pp.train_all(data, label_dict)
    print("--- Total Execution Time for training the dataset : %.3f seconds ---" % (time.time() - start_time))

    return

  def filter_output_test(self):
    prefix = os.path.dirname(os.path.abspath(__file__))
    folder = "data"
    name = "ua_detrac"
    self.input_path = os.path.join(prefix,folder, name, 'small-data', 'MVI_20011', 'img00001.jpg')
    image_width = 960
    image_height = 540
    ratio = 12
    image_width = int(image_width / ratio)
    image_height = int(image_height / ratio)
    channels = 3
    X = np.ndarray(shape=(1, image_height, image_width, channels), dtype=np.float32)


    img = load_img(self.input_path, target_size=(image_height, image_width))
    X[0] = img_to_array(img)

    img1 = array_to_img(X[0])
    save_img(path=os.path.join(prefix, 'examples' , str(9999) + '.jpg'), x=img1, file_format='jpeg')



if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.filter_performance_test()
    #pipeline.filter_output_test()
