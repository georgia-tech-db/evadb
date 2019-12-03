import numpy as np
from src.filters.pp import PP


def test_PP():
    pp = PP()

    labels = ""
    x = np.random.random([2, 30, 30, 3])

    y = {
        'vehicle': [['car', 'car'], ['car', 'car', 'car']],
        'speed': [[6.859 * 5, 1.5055 * 5],
                  [6.859 * 5, 1.5055 * 5, 0.5206 * 5]],
        'color': [None, None],
        'intersection': [None, None]
    }

    stats = pp.train_all(x, y)
