import pickle


class CarType():
    def __init__(self, value):
        self.type = value
        self.model = pickle.load('car_types_model')

    def process(self, data):
        return (self.model.predict(data), self.model.C, self.model.A, self.model.R)
