import pickle


class CarType:
    def __init__(self, value):
        self.type = value
        self.model = pickle.load('car_types_model.pkl')

    def process(self, data):
        return self.model.predict(data), self.model.C, self.model.A, self.model.R


class ColorType:
    def __init__(self, value):
        self.type = value
        self.model = pickle.load('color_types_model.pkl')

    def process(self, data):
        return self.model.predict(data), self.model.C, self.model.A, self.model.R


class SpeedLimit:
    def __init__(self, value):
        self.type = value
        self.model = pickle.load('speed_limit_model.pkl')

    def process(self, data):
        return self.model.predict(data), self.model.C, self.model.A, self.model.R
