
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import sys
from keras.preprocessing.image import img_to_array, load_img, array_to_img, save_img
from faster_rcnn_pytorch.demo import accept_input_from_pp


import loaders.load as load
import filters.pp as pp
import query_optimizer.query_optimizer as qo

try:
  import constants
except:
  sys.path.append("/nethome/jbang36/eva")
  sys.path.append("/home/jaeho-linux/fall2018/DDL/Eva")
  import constants


#TODO: Fill this file in with the components loaded from other files
class Pipeline:
  """1. Load the dataset
     2. Load the QO
     3. Load the Filters
     4. Load the Central Network (RFCNN, SVM for other labels etc)
     5. Listen to Queries
     6. Give back result"""

  def __init__(self):
    self.LOAD = load.Load()
    self.PP = pp.PP()
    self.QO = qo.QueryOptimizer()
    self.data_table = None
    #self.qo = qo.QueryOptimizer()

  def load(self):
    eva_dir = os.path.dirname(os.path.abspath(__file__))
    train_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "train_images")
    test_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "test_images")
    train_anno_dir = os.path.join(eva_dir, "data", "ua_detrac", "train_annotations")


    dir_dict = {"train_image": train_image_dir,
                "test_image": test_image_dir,
                "train_anno": train_anno_dir}
    data_table = self.LOAD.load(dir_dict)
    return data_table

  def run(self):
    self.data_table = self.load()
    self.train()

  def pass_to_udf(self, test_pred, test_X):
    if len(test_X.shape) != 4:
      test_X = test_X.reshape(1, test_X.shape[0], test_X.shape[1], test_X.shape[2])
    pos_frames = np.where(test_pred == 1)
    accept_input_from_pp(test_X[pos_frames])

  def train(self):
    """
    Need to train the PPs and UDF
    :return: trained PPs and UDF
    """
    labels_list = ["image", "vehicle_type", "color", "speed", "intersection"]
    label_of_interest = "vehicle_type"
    data_series = self.data_table[label_of_interest]

    self.pp.train_all(self.data_table) #TODO: Need to fix this function
    #TODO: train UDF - but for now assume it is already trained



  def execute(self):
    TRAF_20 = ["t=suv", "s>60",
                "c=white", "c!=white", "o=pt211", "c=white && t=suv",
                "s>60 && s<65", "t=sedan || t=truck", "i=pt335 && o=pt211",
                "t=suv && c!=white", "c=white && t!=suv && t!=van",
                "t=van && s>60 && s<65", "t=sedan || t=truck && c!=white",
                "i=pt335 && o!=pt211 && o!=pt208", "t=van && i=pt335 && o=pt211",
                "t!=sedan && c!=black && c!=silver && t!=truck",
                "t=van && s>60 && s<65 && o=pt211", "t!=suv && t!=van && c!=red && t!=white",
                "i=pt335 || i=pt342 && o!=pt211 && o!=pt208",
                "i=pt335 && o=pt211 && t=van && c=red"]

    synthetic_pp_list = ["t=car", "t=bus", "t=van", "t=others",
                         "c=red", "c=white", "c=black", "c=silver",
                         "s>40", "s>50", "s>60", "s<65", "s<70",
                         "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                         "o=pt335", "o=pt211", "o=pt342", "o=pt208"]

    load_labels = ["car", "bus", "van", "others",
                   "red", "white", "black","silver",
                   ">40", ">50", ">60", "<65", "<70",
                   "pt335", "pt211", "pt342", "pt208"]

    synthetic_pp_stats = {"t=van": {"none/dnn": {"R": 0.1, "C": 0.1, "A": 0.9},
                                    "pca/dnn": {"R": 0.2, "C": 0.15, "A": 0.92},
                                    "none/kde": {"R": 0.15, "C": 0.05, "A": 0.95}},
                          "t=suv": {"none/svm": {"R": 0.13, "C": 0.01, "A": 0.95}},
                          "t=sedan": {"none/svm": {"R": 0.21, "C": 0.01, "A": 0.94}},
                          "t=truck": {"none/svm": {"R": 0.05, "C": 0.01, "A": 0.99}},

                          "c=red": {"none/svm": {"R": 0.131, "C": 0.011, "A": 0.951}},
                          "c=white": {"none/svm": {"R": 0.212, "C": 0.012, "A": 0.942}},
                          "c=black": {"none/svm": {"R": 0.133, "C": 0.013, "A": 0.953}},
                          "c=silver": {"none/svm": {"R": 0.214, "C": 0.014, "A": 0.944}},

                          "s>40": {"none/svm": {"R": 0.08, "C": 0.20, "A": 0.8}},
                          "s>50": {"none/svm": {"R": 0.10, "C": 0.20, "A": 0.82}},

                          "s>60": {"none/dnn": {"R": 0.12, "C": 0.21, "A": 0.87},
                                   "none/kde": {"R": 0.15, "C": 0.06, "A": 0.96}},

                          "s<65": {"none/svm": {"R": 0.05, "C": 0.20, "A": 0.8}},
                          "s<70": {"none/svm": {"R": 0.02, "C": 0.20, "A": 0.9}},

                          "o=pt211": {"none/dnn": {"R": 0.135, "C": 0.324, "A": 0.993},
                                      "none/kde": {"R": 0.143, "C": 0.123, "A": 0.932}},

                          "o=pt335": {"none/dnn": {"R": 0.134, "C": 0.324, "A": 0.994},
                                      "none/kde": {"R": 0.144, "C": 0.124, "A": 0.934}},

                          "o=pt342": {"none/dnn": {"R": 0.135, "C": 0.325, "A": 0.995},
                                      "none/kde": {"R": 0.145, "C": 0.125, "A": 0.935}},

                          "o=pt208": {"none/dnn": {"R": 0.136, "C": 0.326, "A": 0.996},
                                      "none/kde": {"R": 0.146, "C": 0.126, "A": 0.936}},

                          "i=pt211": {"none/dnn": {"R": 0.135, "C": 0.324, "A": 0.993},
                                      "none/kde": {"R": 0.143, "C": 0.123, "A": 0.932}},

                          "i=pt335": {"none/dnn": {"R": 0.134, "C": 0.324, "A": 0.994},
                                      "none/kde": {"R": 0.144, "C": 0.124, "A": 0.934}},

                          "i=pt342": {"none/dnn": {"R": 0.135, "C": 0.325, "A": 0.995},
                                      "none/kde": {"R": 0.145, "C": 0.125, "A": 0.935}},

                          "i=pt208": {"none/dnn": {"R": 0.136, "C": 0.326, "A": 0.996},
                                      "none/kde": {"R": 0.146, "C": 0.126, "A": 0.936}}}

    label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
                  "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
                  "c": [constants.DISCRETE, ["white", "red", "black", "silver"]],
                  "i": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]],
                  "o": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]]}


    for query in TRAF_20:
      qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)

    self.pass_to_udf(np.asarray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), img)



  """
  # We have access to train and test dataset -> Used for finding the score and evaluation
  def test(self):
    start_time = time.time()

    data, label_dict = self.LOAD.load_dataset()
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
    
  """

  def save_image(self, xs, description):
    project_path = os.path.dirname(os.path.abspath(__file__))
    count = 100
    for x in xs:
      img1 = array_to_img(x)
      save_img(path=os.path.join(project_path, 'examples', str(count) + '.jpg'), x=img1, file_format='jpeg')
      count += 1
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
    pipeline.run()


    # the actual pipeline will be train -> execute
    #pipeline.load() TODO
    #pipeline.train() # this function should train all the PPs and UDFs TODO
    #pipeline.execute() # this function should be query -> QO -> PP -> UDFs -> Output TODO
