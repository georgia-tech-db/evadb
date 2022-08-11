import os

from eva.udfs.gaussian_blur import GaussianBlur

from test.udfs.test_utils import load_image, get_udf_data_path

def test_gaussian_blur():
    img_path = os.path.join(get_udf_data_path(), "dog.jpeg")
    print(img_path)
    img = load_image(img_path)

    blur = GaussianBlur(kernel_size=3, sigma=0.5)

    blurred_img = blur.transform(img)
    assert len(img) == len(blurred_img)