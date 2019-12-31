import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_dir = os.path.join(root, "test", "data", "uadetrac", "small-data")
anno_dir = os.path.join(root, "test", "data", "uadetrac", "small-annotations")

try:
    from src.loaders.loader_uadetrac import UADetracLoader
except ImportError:
    sys.path.append(root)
    from src.loaders.loader_uadetrac import UADetracLoader


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
    assert labels == loader.labels


def test_load_boxes():
    loader = UADetracLoader(None, 400, 400)
    width_scale = 400 / 960
    height_scale = 400 / 540
    loader.load_boxes(anno_dir)

    top = int(378.8 * height_scale)
    left = int(592.75 * width_scale)
    bottom = int((378.8 + 162.2) * height_scale)
    right = int((592.75 + 160.05) * width_scale)
    box = [top, left, bottom, right]

    print(loader.boxes[0])
    assert loader.boxes[0][0] == box
