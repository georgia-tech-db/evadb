import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.loaders.uadetrac_loader import UADetracLoader
except ImportError:
    sys.path.append(root)
    from src.loaders.uadetrac_loader import UADetracLoader


def test():
    image_dir = root + "/test/data/small-data"
    print(image_dir)
    loader = UADetracLoader(None, 400, 400)
    loader.load_images(image_dir)
    assert loader.images.shape == (9, 400, 400, 3)
