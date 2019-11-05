import numpy as np
from src.filters.minimum_filter import FilterMinimum

class abstract_PP_filter_template:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        
    def predict(self, batch):
        predictions = self.model.predict(batch)
        required_frame_ids = []
        for i, prediction in enumerate(predictions):
            if prediction:
                required_frame_ids.append(i)
        return batch[required_frame_ids]



