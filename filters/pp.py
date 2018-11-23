from kdewrapper import KernelDensityWrapper
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPClassifier

# Meant to be a black box for trying all models available and returning statistics and model for
# the query optimizer to choose for a given query

class PP:
  def __init__(self):

    self.model_library = {"kde": self.kde,
                          "svm": self.svm,
                          "dnn": self.dnn,
                          "rf": self.rf} #KDE, SVM, NN - this should be a mapping of model name to model CONSTRUCTOR

    self.pre_model_library = {"none": self.none,
                              "pca": self.pca,
                              #"fh": self.feature_hashing,
                              # "sampling": self.sampling,
                              } #feature hashing, PCA, None - Separated to do mix and match

    #self.pre_results = {} #save the preprocessed results {"pre_model_name": reformed_data
    self.category_library = {} #save the trained model
    self.category_stats = {} #save the statistics related to the model, although most stats are embedded in the model,
                             #made this just in case there could be stats that are not saved
    self.pre_category_library = {}

  def train_all(self, X, label_dict):
    X_preprocessed = self.preprocess(X, label_dict)
    self.process(X_preprocessed, label_dict)

  def process(self, X, label_dict):
    for process_method in X:
      for model in self.model_library:
        self.model_library[model]([X[process_method], label_dict, process_method])


  def preprocess(self, X, label_dict):
    X_preprocessed = {}
    for model in self.pre_model_library:
      X_preprocessed[model], _ = self.pre_model_library[model]([X,label_dict])
    return X_preprocessed

  def evaluate(self, X_test, label_dict):
    """

    self.category_stats[category_name] = {model_name: {"reduction_rate": model.score(),
                                                       "false_negative_rate": model.......,
                                                       "time_to_train":}
    """
    #TODO: need to include various categories in self.category_stats, but will only include the accuracy for now
    for category_name in self.category_library:
      for model_name in self.category_library[category_name]:
        #We need to parse by "/" token and apply the proper preprocessing method
        pre, pro = model_name.split("/")
        X_pre, _ = self.pre_model_library[pre]([X_test, label_dict])
        model = self.category_library[category_name][model_name]
        score = model.score(X_pre, label_dict[category_name])
        if category_name not in self.category_stats:
          self.category_stats[category_name] = {}

        self.category_stats[category_name][model_name] = {"score": score}

    return self.category_stats

  #random forest
  def rf(self, args):
    X, label_dict, pre = args
    for label in label_dict:
      rf = RandomForestClassifier(max_depth=2, random_state=0)
      rf.fit(X, label_dict[label])
      if label not in self.category_library:
        self.category_library[label] = {}
      self.category_library[label][pre + '/rf'] = rf


  def dnn(self, args):
    X, label_dict, pre = args
    for label in label_dict:
      dnn = MLPClassifier(solver='lbfgs', alpha=1e-5,
                          hidden_layer_sizes = (5, 2), random_state = 1)
      dnn.fit(X, label_dict[label])
      if label not in self.category_library:
        self.category_library[label] = {}
      self.category_library[label][pre +'/dnn'] = dnn
    return

  def svm(self, args):
    X, label_dict, pre = args
    for label in label_dict:
      svm = LinearSVC(random_state=0)
      svm.fit(X, label_dict[label])
      if label not in self.category_library:
        self.category_library[label] = {}
      self.category_library[label][pre + '/svm'] = svm
    return

  def kde(self, args):
    X, label_dict, pre = args
    for label in label_dict:
      kde = KernelDensityWrapper(kernel='gaussian', bandwidth=0.2)
      # We will assume each label is one-shot encoding
      kde.fit(X, label_dict[label])
      if label not in self.category_library:
        self.category_library[label] = {}
      self.category_library[label][pre + '/kde'] = kde

    return

  def pca(self, args):
    X, label_dict = args
    if "pca" not in self.pre_category_library:
      pca = PCA()
      X_new = pca.fit_transform(X)
      self.pre_category_library["pca"] = pca
    else:
      pca = self.pre_category_library["pca"]
      X_new = pca.transform(X)

    return [X_new, label_dict] #we will return the models for the caller to save them


  # According to paper, each pixel or blob of 8x8 can be mapped to a dimension
  # We will first try to make each pixel a dimension
  # It is told that if feature vector is dense, accuracy becomes worse
  # Will not do for now...
  def feature_hashing(self, args):
    """
    category_count = len(self.category_libary.keys())
    if category_count < 2:
      return

    h = FeatureHasher(n_features=category_count)
    D = [{'dog': 1, 'cat': 2, 'elephant': 4}, {'dog': 2, 'run': 5}]
    f = h.transform(D)
    f.toarray()
    """
    return args

  def sampling(self, args):
    pass

  def none(self, args):
    return args


  def getCategoryInfo(self, category_name):
    return self.category_stats[category_name]

  def getCategoryModels(self, category_name):
    return self.category_library[category_name]

  # returns list of model names
  def getModelLibrary(self):
    return self.model_library.keys()










