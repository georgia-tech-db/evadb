class AbstractPPTemplate:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self._init_model()

    def _init_model(self):
        return None

    def predict(self, batch):
        predictions = self.model.predict(batch)
        required_frame_ids = []
        for i, prediction in enumerate(predictions):
            if prediction:
                required_frame_ids.append(i)
        return batch[required_frame_ids]
