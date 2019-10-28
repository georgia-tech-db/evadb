import pickle
class CarType():
    def __init__(self, value):
        self.type = value

    def process(self, data):
        model = pickle.load('car_types_model')
        return model.process(data)
