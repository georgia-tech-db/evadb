from PIL import Image
import numpy as np
import glob
import os
from src.models import FrameBatch


class DepthAndFrameLoader():

    def __init__(self, images_folder_path, depths_folder_path):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.images_folder_path = self.base_path + images_folder_path
        self.depths_folder_path = self.base_path + depths_folder_path

    def _load_data_from_folder(self, folder, isDepth=False):
        """
        Returns a numpy array with images from a folder path

        arguments:
        folder: path of the folder where images are stored
        isDepth: True if attempting to retrieve depth data

        """

        filelist = glob.glob(folder + '/*.png')
        data = []
        for fname in filelist:
            png = np.array(Image.open(fname), dtype=int)
            if isDepth:
                # make sure we have a proper 16bit depth map here.. not 8bit!
                assert(np.max(png) > 255)
                depth = png.astype(np.float) / 256.
                depth[png == 0] = -1.
                data.append(depth)
            else:
                data.append(png)
        return np.asarray(data)

    def load_data(self):
        """
        method to load images and depth
        base_path: file location root path
        num_images: number of images to load, image names have to be in format
        0.png, 1.png ... num_images.png
                    both for depth and RGB images
        returns
            Framebatch object containing all the frames
            Depth images in numpy array
        """

        images = self._load_data_from_folder(self.images_folder_path)
        depths = self._load_data_from_folder(self.depths_folder_path, True)

        return FrameBatch(images, None), np.array(depths)


if __name__ == '__main__':
    images_folder_path = "/data/images"
    depths_folder_path = "/data/depths"

    # create an object of loader, pass folder path where images are stored
    loader = DepthAndFrameLoader(images_folder_path, depths_folder_path)
    _, _ = loader.load_data()
