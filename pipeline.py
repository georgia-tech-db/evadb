

import filters.load.Load as Load
import filters.pp.PP as PP





#TODO: Fill this file in with the components loaded from other files
class Pipeline:
    """1. Load the dataset
       2. Load the QO
       3. Load the Filters
       4. Load the Central Network (RFCNN, SVM for other labels etc)
       5. Listen to Queries
       6. Give back result"""



    def __init__(self):
        load = Load()
        pp = PP()



    def run(self):
        pass





if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()

