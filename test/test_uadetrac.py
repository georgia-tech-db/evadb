import sys

sys.path.append('../')
from src.loaders.uadetrac_loader import UADetracLoader


def test():
    image_dir = "./data/small-data"
    loader = UADetracLoader(None, 400, 400)
    loader.load_images(image_dir)
    assert loader.images.shape == (9, 400, 400, 3)
