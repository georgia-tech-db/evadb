import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_dir = root + "/test/data/small-data"
anno_dir = root + "/test/data/small-annotations"

try:
    from src.loaders.uadetrac_loader import UADetracLoader
except ImportError:
    sys.path.append(root)
    from src.loaders.uadetrac_loader import UADetracLoader


def test_load_images():
    loader = UADetracLoader(None, 400, 400)
    loader.load_images(image_dir)
    assert loader.images.shape == (9, 400, 400, 3)


def test_load_annotations1():
    loader = UADetracLoader(None, 400, 400)
    labels = loader.load_labels(anno_dir)
    assert labels is None


def test_load_annotations2():
    loader = UADetracLoader(None, 400, 400)
    loader.load_images(image_dir)
    loader.load_labels(anno_dir)
    labels = {
        'vehicle': [['car', 'car'], ['car', 'car', 'car']],
        'speed': [[6.859 * 5, 1.5055 * 5],
                  [6.859 * 5, 1.5055 * 5, 0.5206 * 5]],
        'color': [None, None],
        'intersection': [None, None]
    }
    print(loader.labels)
    print(labels)
    assert labels == loader.labels
