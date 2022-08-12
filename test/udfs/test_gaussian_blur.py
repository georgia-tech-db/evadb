import os
import PIL

import torch

from eva.udfs.gaussian_blur import GaussianBlur

from test.udfs.test_utils import load_image, get_udf_data_path


def test_gaussian_blur_PIL():
    img_path = os.path.join(get_udf_data_path(), "dog.jpeg")
    img = PIL.Image.fromarray(load_image(img_path))

    blur = GaussianBlur(kernel_size=3, sigma=0.5)

    blurred_img = blur.transform(img)
    assert type(img) == type(blurred_img)


def test_gaussian_blur_on_torch_array():
    arr = torch.ones((3, 10, 10))

    blur = GaussianBlur(kernel_size=3, sigma=0.5)

    blurred_arr = blur.transform(arr)

    assert arr.shape == blurred_arr.shape
