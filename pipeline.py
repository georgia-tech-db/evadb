
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import sys
from keras.preprocessing.image import img_to_array, load_img, array_to_img, save_img
#from faster_rcnn_pytorch.demo import accept_input_from_pp


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
    self.image_matrix_train = None
    self.image_matrix_test = None
    self.data_table_train = None
    self.data_table_test = None
    #self.qo = qo.QueryOptimizer()


  def run(self):
    image_matrix, data_table = self.load()
    self.image_matrix_train, self.image_matrix_test, self.data_table_train, self.data_table_test = self._split_train_val(image_matrix, data_table)
    self.train()
    pp_category_stats = self.PP.getCategoryStats()
    pp_models = self.PP.getCategoryModel()
    self.execute(pp_category_stats, pp_models)


  def _split_train_val(self, X, label_dict):
    n_samples, _, _, _= X.shape
    mixed_indices = np.random.permutation(n_samples)
    train_index_end = int(len(mixed_indices) * 0.8)

    X_train = X[mixed_indices[:train_index_end]]
    X_test = X[mixed_indices[train_index_end:]]


    label_dict_train = {}
    label_dict_test = {}
    for column in label_dict:
        label_dict_train[column] = label_dict[column][mixed_indices[:train_index_end]]
        label_dict_test[column] = label_dict[column][mixed_indices[train_index_end:]]

    return X_train, X_test, label_dict_train, label_dict_test


  def load(self):
    eva_dir = os.path.dirname(os.path.abspath(__file__))
    train_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "tiny-data")
    #test_image_dir = os.path.join(eva_dir, "data", "ua_detrac", "test_images")
    train_anno_dir = os.path.join(eva_dir, "data", "ua_detrac", "tiny-annotation")

    dir_dict = {"train_image": train_image_dir,
                "train_anno": train_anno_dir,
                "test_image": None}
    image_matrix, train_data_table, test_data_table = self.LOAD.load(dir_dict)
    return image_matrix, train_data_table



  def pass_to_udf(self, test_pred, test_X):
    if len(test_X.shape) != 4:
      test_X = test_X.reshape(1, test_X.shape[0], test_X.shape[1], test_X.shape[2])
    pos_frames = np.where(test_pred == 1)
    #accept_input_from_pp(test_X[pos_frames])

  def train(self):
    """
    Need to train the PPs and UDF
    :return: trained PPs and UDF
    """
    labels_list = ["image", "vehicle_type", "color", "speed", "intersection"]
    label_of_interest = "vehicle_type"


    pp_category_stats = self.PP.train_all(self.image_matrix_train, self.data_table_train) #TODO: Need to fix this function
    #TODO: train UDF - but for now assume it is already trained
    #TODO: Need to get the trained result and feed into the query optimizer
    #TODO: Make query optimizer execute TRAF_20 queries
    #TODO: Use the pipeline and UDF to filter results
    return pp_category_stats

  def execute(self, pp_category_stats, pp_category_models):
    TRAF_20 = ["t=van", "s>60",
                "c=white", "c!=white", "o=pt211", "c=white && t=van",
                "s>60 && s<65", "t=car || t=others", "i=pt335 && o=pt211",
                "t=van && c!=white", "c=white && t!=van && t!=car",
                "t=van && s>60 && s<65", "t=car || t=others && c!=white",
                "i=pt335 && o!=pt211 && o!=pt208", "t=van && i=pt335 && o=pt211",
                "t!=car && c!=black && c!=silver && t!=others",
                "t=van && s>60 && s<65 && o=pt211", "t!=sedan && t!=van && c!=red && t!=white",
                "i=pt335 || i=pt342 && o!=pt211 && o!=pt208",
                "i=pt335 && o=pt211 && t=van && c=red"]


    synthetic_pp_list = ["t=car", "t=bus", "t=van", "t=others",
                         "c=red", "c=white", "c=black", "c=silver",
                         "s>40", "s>50", "s>60", "s<65", "s<70",
                         "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                         "o=pt335", "o=pt211", "o=pt342", "o=pt208"]


    label_desc = {"t": [constants.DISCRETE, ["car", "others", "bus", "van"]],
                  "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
                  "c": [constants.DISCRETE, ["white", "red", "black", "silver"]],
                  "i": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]],
                  "o": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]]}


    query_plans = []
    for query in TRAF_20:
    #TODO: After running the query optimizer, we want the list of PPs to work with
    #TODO: Then we want to execute the queries with the PPs and send it to the UDF after
      best_query, best_operators, reduction_rate = self.QO.run(query, synthetic_pp_list, pp_category_stats, label_desc)
    #TODO: Assume the best_query is in the form ["(PP_name, model_name) , (PP_name, model_name), (PP_name, model_name), (PP_name, model_name), (UDF_name, model_name - None)]
    #                                   operators will be [np.logical_and, np.logical_or, np.logical_and.....]
      if __debug__:
        print("The total reduction rate associated with the query is " + str(reduction_rate))
        print("The best alternative for " + query + " is " + str(best_query))
        print("The operators involved are " + str(best_operators))
      y_hat1 = []
      y_hat2 = []
      for i in xrange(len(best_query)):
        pp_name, model_name = best_query[i]
        if y_hat1 == []:
          y_hat1 = self.PP.predict(self.image_matrix_test, pp_name, model_name)
          continue
        else:
          y_hat2 = self.PP.predict(self.image_matrix_test, pp_name, model_name)
          y_hat1 = best_operators[i - 1](y_hat1, y_hat2)

      print ("The final boolean array to pass to udf is : \n" + str(y_hat1))
      #result = self.pass_to_udf(X[y_hat1])

    """
      y_hat1 = []
      y_hat2 = []
      for i in xrange len(best_query):
        pp_name, model_name = best_query[i]
        if y_hat1 == []:
            y_hat1 = self.PP.predict(self.image_table, pp_name, model_name)
            continue
        else:
            y_hat2 = self.PP.predict(self.image_table, pp_name, model_name)
            y_hat1 = operators_returned_from_qorun[i-1](y_hat1, y_hat2)
    
      # Now indices we need for this query is complete
      # result = pass_to_udf(X[y_hat1])
      # save_result -- this may be in the form of images??
        
    
    """

    #self.pass_to_udf(np.asarray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), img)



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
