import os
import sys

import numpy as np

from src import filters as pp, constants
import loaders.load as load
import query_optimizer.query_optimizer as qo

try:
    pass
except ImportError:
    sys.path.append("/nethome/jbang36/eva")
    sys.path.append("/home/jaeho-linux/fall2018/DDL/Eva")
    import src.constants


# TODO: Fill this file in with the components loaded from other files
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
        # self.qo = qo.QueryOptimizer()

    def run(self):
        print("Loading data....")
        image_matrix, data_table = self.load()
        self.image_matrix_train, self.image_matrix_test, \
            self.data_table_train, self.data_table_test = \
            self._split_train_val(image_matrix, data_table)
        print("Training data....")
        self.train()
        pp_category_stats = self.PP.getCategoryStats()
        pp_models = self.PP.getCategoryModel()
        print("Evaluating data....")
        self.execute(pp_category_stats, pp_models)

    def _split_train_val(self, X, label_dict):
        n_samples, _, _, _ = X.shape
        mixed_indices = np.random.permutation(n_samples)
        train_index_end = int(len(mixed_indices) * 0.8)

        X_train = X[mixed_indices[:train_index_end]]
        X_test = X[mixed_indices[train_index_end:]]

        label_dict_train = {}
        label_dict_test = {}
        for column in label_dict:
            label_dict_train[column] = label_dict[column][
                mixed_indices[:train_index_end]]
            label_dict_test[column] = label_dict[column][
                mixed_indices[train_index_end:]]

        return X_train, X_test, label_dict_train, label_dict_test

    def load(self):
        eva_dir = os.path.dirname(os.path.abspath(__file__))
        train_image_dir = os.path.join(eva_dir, "data", "ua_detrac",
                                       "tiny-data")
        train_anno_dir = os.path.join(eva_dir, "data", "ua_detrac",
                                      "tiny-annotations")

        dir_dict = {"train_image": train_image_dir,
                    "train_anno": train_anno_dir,
                    "test_image": None}
        image_matrix, train_data_table, test_data_table = self.LOAD.load(
            dir_dict)
        return image_matrix, train_data_table

    def pass_to_udf(self, labels, column_name):
        print("Inside pass_to_udf, currently we don't have any UDF installed")
        return
        # return accept_input_from_pp(self.image_matrix_test, labels,
        # column_name)

    def train(self):
        """
        Need to train the PPs and UDF
        :return: trained PPs and UDF
        """
        labels_list = ["image", "vehicle_type", "color", "speed",
                       "intersection"]
        label_of_interest = "vehicle_type"

        pp_category_stats = self.PP.train_all(self.image_matrix_train,
                                              self.data_table_train)  #
        # TODO: Need to fix this function
        # TODO: train UDF - but for now assume it is already trained
        # TODO: Need to get the trained result and feed into the query
        #  optimizer
        # TODO: Make query optimizer execute TRAF_20 queries
        # TODO: Use the pipeline and UDF to filter results
        return pp_category_stats

    def execute(self, pp_category_stats, pp_category_models):
        TRAF_20 = ["t=van", "s>60",
                   "c=white", "c!=white", "o=pt211", "c=white && t=van",
                   "s>60 && s<65", "t=car || t=others", "i=pt335 && o=pt211",
                   "t=van && c!=white", "c=white && t!=van && t!=car",
                   "t=van && s>60 && s<65", "t=car || t=others && c!=white",
                   "i=pt335 && o!=pt211 && o!=pt208",
                   "t=van && i=pt335 && o=pt211",
                   "t!=car && c!=black && c!=silver && t!=others",
                   "t=van && s>60 && s<65 && o=pt211",
                   "t!=sedan && t!=van && c!=red && t!=white",
                   "i=pt335 || i=pt342 && o!=pt211 && o!=pt208",
                   "i=pt335 && o=pt211 && t=van && c=red"]

        synthetic_pp_list = ["t=car", "t=bus", "t=van", "t=others",
                             "c=red", "c=white", "c=black", "c=silver",
                             "s>40", "s>50", "s>60", "s<65", "s<70",
                             "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                             "o=pt335", "o=pt211", "o=pt342", "o=pt208"]

        label_desc = {
            "t": [constants.DISCRETE, ["car", "others", "bus", "van"]],
            "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
            "c": [constants.DISCRETE, ["white", "red", "black", "silver"]],
            "i": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]],
            "o": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]]}

        query_plans = []
        for query in TRAF_20:
            # TODO: After running the query optimizer, we want the list of
            #  PPs to work with
            # TODO: Then we want to execute the queries with the PPs and
            #  send it to the UDF after
            best_query, best_operators, reduction_rate = self.QO.run(
                query, synthetic_pp_list, pp_category_stats, label_desc)
            # TODO: Assume the best_query is in the form ["(PP_name,
            #  model_name) , (PP_name, model_name), (PP_name, model_name),
            #  (PP_name, model_name), (UDF_name, model_name - None)]
            #                                   operators will be [
            #                                   np.logical_and,
            #                                   np.logical_or,
            #                                   np.logical_and.....]
            if __debug__:
                print(
                    "The total reduction rate associated with the query is "
                    + str(
                        reduction_rate))
                print(("The best alternative for " + query + " is " + str(
                    best_query)))
                print(("The operators involved are " + str(best_operators)))
            y_hat1 = []
            y_hat2 = []
            for i in range(len(best_query)):
                pp_name, model_name = best_query[i]
                if y_hat1 == []:
                    y_hat1 = self.PP.predict(self.image_matrix_test, pp_name,
                                             model_name)
                    continue
                else:
                    y_hat2 = self.PP.predict(self.image_matrix_test, pp_name,
                                             model_name)
                    y_hat1 = best_operators[i - 1](y_hat1, y_hat2)

            print(("The final boolean array to pass to udf is : \n" + str(
                y_hat1)))

            if "t=" in query and query in self.data_table_test:
                resulting_labels = self.pass_to_udf(y_hat1,
                                                    query.replace("t=", ""))
                print(("Total score for this query is " + str(
                    np.sum(
                        resulting_labels == self.data_table_test[query]) / len(
                        resulting_labels))))
            else:
                print(("No existing udf for this query: " + query))


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()

    # the actual pipeline will be train -> execute
    # pipeline.load() TODO
    # pipeline.train() # this function should train all the PPs and UDFs TODO
    # pipeline.execute() # this function should be query -> QO -> PP -> UDFs
    # -> Output TODO
