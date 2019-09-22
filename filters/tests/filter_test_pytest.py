import random

import numpy as np
from sklearn.neural_network import MLPClassifier

from filters.pp import PP

# TODO: FIX TEST CASES

# def test_normalization():
#     input_path = '../data/ua_detrac/small-data/'
#     # input_path="../images"
#     X, num_frames_list = load_dataset(input_path)
#     ind = random.randint(0, len(X))
#     img = np.asarray(X[ind])
#     if np.min(img) > 1 or np.min(img) < -1:
#         assert False
#     elif np.max(img) > 1 or np.max(img) < -1:
#         assert False
#     assert True


# def test_get_vehtype_labels(filter, label_path):
#     input_path = '../data/ua_detrac/small-data/'
#     # input_path="../images"
#     X, num_frames_list = load_dataset(input_path)
#     y = get_vehtype_labels(filter, label_path, num_frames_list)
#
#     if (y[0] != 1):
#         assert False
#     assert True
#     TODO: Create test cases for ending frames absent in xml and
#      intermediate frames absent in xml. Small Data passes these two
#      conditions all the time.


# def test_rf():
#     input_path = '../data/ua_detrac/small-data/'
#     annotation_path = "../data/ua_detrac/small-annotation"
#     X, num_frames_list = load_dataset(input_path)
#     y = get_vehtype_labels('car', annotation_path, num_frames_list)
#     obj = PP()
#     try:
#         obj.rf([X.reshape(X.shape[0], -1), {'veh_type': y}, 'none'])
#         if obj.category_library['veh_type'][
#             'none/rf'] == None or not isinstance(
#             obj.category_library['veh_type']['none/rf'],
#             RandomForestClassifier):
#             assert False
#     except Exception as e:
#         assert False
#     # obj.rf()
#     # if obj.category_library['veh_type']['/rf']==None:
#     #    assert False
#     assert True


# def test_dnn():
#     input_path = '../data/ua_detrac/small-data/'
#     annotation_path = "../data/ua_detrac/small-annotation"
#     X, num_frames_list = load_dataset(input_path)
#     y = get_vehtype_labels('car', annotation_path, num_frames_list)
#     obj = PP()
#     try:
#         obj.dnn([X.reshape(X.shape[0], -1), {'veh_type': y}, 'none'])
#         if obj.category_library['veh_type'][
#             'none/dnn'] == None or not isinstance(
#             obj.category_library['veh_type']['none/dnn'], MLPClassifier):
#             assert False
#     except Exception as e:
#         assert False
#     # obj.rf()
#     # if obj.category_library['veh_type']['/rf']==None:
#     #    assert False
#     assert True
#
#
# def test_pca():
#     input_path = '../data/ua_detrac/small-data/'
#     annotation_path = "../data/ua_detrac/small-annotation"
#     X, num_frames_list = load_dataset(input_path)
#     y = get_vehtype_labels('car', annotation_path, num_frames_list)
#     obj = PP()
#     try:
#         n_components = 135
#         li = obj.pca(
#             [X.reshape(X.shape[0], -1), {'veh_type': y}, n_components])
#         X = li[0]
#         if X.shape[1] != n_components:
#             assert False
#     except Exception as e:
#         assert False
#     assert True
#
#
# test_dnn()
# test_normalization()
# test_get_vehtype_labels('car','../data/ua_detrac/small-annotation')
