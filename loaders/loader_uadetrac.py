"""
This file implements the dataset loading methods for UA-detrac
If any problem occurs, please email jaeho.bang@gmail.com


@Jaeho Bang

"""

import argparse
import os
import warnings
import xml.etree.ElementTree as ET

import cv2
import numpy as np
import pandas as pd

from loaders import TaskManager
from loaders.loader_template import LoaderTemplate

parser = argparse.ArgumentParser(description='Define arguments for loader')
parser.add_argument('--image_path', default='small-data', help='Define data folder within eva/data/uadetrac')
parser.add_argument('--anno_path', default='small-annotations',
                    help='Define annotation folder within eva/data/uadetrac')
parser.add_argument('--save_path', default='npy_files', help='Define save folder for images, annotations, boxes')

args = parser.parse_args()


# Make this return a dictionary of label to data for the whole dataset

class LoaderUADetrac(LoaderTemplate):
    def __init__(self, image_width=300, image_height=300):
        self.data_dict = {}
        self.label_dict = {}
        self.vehicle_type_filters = ['car', 'van', 'bus', 'others']
        self.speed_filters = [40, 50, 60, 65, 70]
        self.intersection_filters = ["pt335", "pt342", "pt211", "pt208"]
        self.color_filters = ['white', 'black', 'silver', 'red']

        ## original image height = 540
        ## original image width = 960
        self.image_width = image_width
        self.image_height = image_height
        self.image_channels = 3
        self.task_manager = TaskManager.TaskManager()
        self.images = None
        self.eva_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load_video(self, dir: str):
        """
        This function is not needed for ua_detrac
        Should never be called
        :return: None
        """
        return None

    def load_boxes(self, dir: str = None):
        """
        Loads boxes from annotation
        Should be same shape as self.labels
        :return: boxes
        """
        if dir == None:
            dir = os.path.join(self.eva_dir, 'data', 'ua_detrac', args.anno_path)
        self.boxes = self.get_boxes(dir)
        return self.boxes

    def load_images(self, dir: str = None):
        """
        This function simply loads image of given image
        :return: image_array (numpy)
        """
        if dir == None:
            dir = os.path.join(self.eva_dir, 'data', 'ua_detrac', args.image_path)
        file_names = []
        for root, subdirs, files in os.walk(dir):
            files.sort()
            for file in files:
                file_names.append(os.path.join(root, file))
        print("Number of files added: ", len(file_names))

        self.images = np.ndarray(shape=(
            len(file_names), self.image_height, self.image_width, self.image_channels),
            dtype=np.uint8)

        for i in range(len(file_names)):
            file_name = file_names[i]
            img = cv2.imread(file_name)
            img = cv2.resize(img, (self.image_width, self.image_height))
            self.images[i] = img

        return self.images

    def load_labels(self, dir: str = None):
        """
        Loads vehicle type, speed, color, and intersection of ua-detrac
        vehicle type, speed is given by the dataset
        color, intersection is derived from functions built-in
        :return: labels
        """

        if dir == None:
            dir = os.path.join(self.eva_dir, 'data', 'ua_detrac', args.anno_path)
        results = self._load_XML(dir)
        if results is not None:
            vehicle_type_labels, speed_labels, color_labels, intersection_labels = results
            return {'vehicle': vehicle_type_labels, 'speed': speed_labels,
                    'color': color_labels, 'intersection': intersection_labels}
        else:
            return None

    def save_images(self):
        save_dir = os.path.join(self.eva_dir, 'data', args.save_path, 'ua_detrac_images.npy')
        if self.images == None:
            warnings.warn("No image loaded, call load_images() first", Warning)
        elif type(self.images) is np.ndarray:
            np.save(save_dir, self.images)
        else:
            warnings.warn("Image array type is not np.....cannot save", Warning)
            np.save(save_dir, self.images)

    def save_labels(self):
        save_dir = os.path.join(self.eva_dir, 'data', args.save_path, 'ua_detrac_labels.npy')
        if self.images == None:
            warnings.warn("No labels loaded, call load_labels() first", Warning)
        elif type(self.labels) is np.ndarray:
            np.save(save_dir, self.labels)
        else:
            warnings.warn("Labels type is not np....cannot save", Warning)

    def save_boxes(self):
        save_dir = os.path.join(self.eva_dir, 'data', args.save_path, 'ua_detrac_boxes.npy')
        if self.images == None:
            warnings.warn("No labels loaded, call load_boxes() first", Warning)
        elif type(self.images) is np.ndarray:
            np.save(save_dir, self.boxes)
        else:
            warnings.warn("Labels type is not np....cannot save", Warning)

    def get_boxes(self, anno_dir):
        width = self.image_width
        height = self.image_height
        import xml.etree.ElementTree as ET
        original_height = 540
        original_width = 960
        anno_files = os.listdir(anno_dir)
        anno_files.sort()
        boxes_dataset = []
        cumu_count = 0

        for anno_file in anno_files:
            if ".xml" not in anno_file:
                print("skipping", anno_file)
                continue
            file_path = os.path.join(anno_dir, anno_file)

            tree = ET.parse(file_path)
            tree_root = tree.getroot()

            for frame in tree_root.iter('frame'):
                boxes_frame = []
                curr_frame_num = int(frame.attrib['num'])
                if len(boxes_dataset) < cumu_count + curr_frame_num - 1:
                    boxes_dataset.extend([None] * (cumu_count + curr_frame_num - len(boxes_dataset)))
                    boxes_dataset.append()
                for box in frame.iter('box'):
                    left = int(float(box.attrib['left']) * width / original_width)
                    top = int(float(box.attrib['top']) * height / original_height)
                    right = int((float(box.attrib['left']) + float(box.attrib['width'])) * width / original_width)
                    bottom = int((float(box.attrib['top']) + float(box.attrib['height'])) * height / original_height)

                    boxes_frame.append((top, left, bottom, right))

                boxes_dataset.append(boxes_frame)

        return boxes_dataset

    def _convert_speed(self, original_speed):
        """
        TODO: Need to actually not use this function, because we need to find out what the original speed values mean
        TODO: However, in the meantime, we will use this extrapolation....
        :param original_speed:
        :return: converted_speed
        """
        speed_range = [0.0, 20.0]
        converted_range = [0.0, 100.0]

        return original_speed * 5

    def _load_XML(self, directory):
        """
        UPDATE: vehicle colors can now be extracted through the xml files!!! We will toss the color generator
        :param directory:
        :return:
        """
        car_labels = []
        speed_labels = []
        color_labels = []
        intersection_labels = []
        if self.images is None:
            warnings.warn("Must load image before loading labels...returning", Warning)
            return None

        print("walking", directory, "for xml parsing")
        for root, subdirs, files in os.walk(directory):
            files.sort()
            for file in files:
                file_path = os.path.join(root, file)
                if ".swp" in file_path:
                    continue
                tree = ET.parse(file_path)
                tree_root = tree.getroot()
                start_frame_num = 1
                start_frame = True
                for frame in tree_root.iter('frame'):
                    curr_frame_num = int(frame.attrib['num'])
                    if start_frame and curr_frame_num != start_frame_num:
                        car_labels.append([None] * (curr_frame_num - start_frame_num))
                        speed_labels.append([None] * (curr_frame_num - start_frame_num))

                    car_per_frame = []
                    speed_per_frame = []
                    color_per_frame = []
                    intersection_per_frame = []

                    bboxes = []
                    for box in frame.iter('box'):
                        left = int(eval(box.attrib['left']))
                        top = int(eval(box.attrib['top']))
                        right = left + int(eval(box.attrib['width']))
                        bottom = top + int(eval(box.attrib['height']))
                        bboxes.append([left, top, right, bottom])
                    # curr_frame_num -1 comes from the fact that indexes start from 0 whereas the start_frame_num = 1

                    scene = file.replace(".xml", "")  # MVI_20011.xml -> MVI_20011
                    intersection_per_frame = self.task_manager.call_intersection(self.images[curr_frame_num - 1], scene,
                                                                                 bboxes)

                    for att in frame.iter('attribute'):
                        if (att.attrib['vehicle_type']):
                            car_per_frame.append(att.attrib['vehicle_type'])
                        if (att.attrib['speed']):
                            speed_per_frame.append(self._convert_speed(float(att.attrib['speed'])))
                        if (att.attrib['color']):
                            color_per_frame.append(att.attrib['color'])
                    assert (len(car_per_frame) == len(speed_per_frame))
                    assert (len(car_per_frame) == len(color_per_frame))
                    assert (len(car_per_frame) == len(intersection_per_frame))

                    if len(car_per_frame) == 0:
                        car_labels.append(None)
                    else:
                        car_labels.append(car_per_frame)

                    if len(speed_per_frame) == 0:
                        speed_labels.append(None)
                    else:
                        speed_labels.append(speed_per_frame)

                    if len(color_per_frame) == 0:
                        color_labels.append(None)
                    else:
                        color_labels.append(color_per_frame)

                    if len(intersection_per_frame) == 0:
                        intersection_labels.append(None)
                    else:
                        intersection_labels.append(intersection_per_frame)

                    start_frame = False

        return [car_labels, speed_labels, color_labels, intersection_labels]

    @staticmethod
    def image_eval(image_str):
        warnings.warn("deprecated", DeprecationWarning)
        image_str = ' '.join(image_str.split())
        image_str = image_str.replace(" ", ",")
        image_str = image_str[0] + image_str[2:]
        evaled_image = np.array(eval(image_str))
        height = 540
        width = 960
        channels = 3
        return evaled_image.reshape(height, width, channels)

    @staticmethod
    def load_from_csv(filename):
        warnings.warn("deprecated", DeprecationWarning)
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_dir = os.path.join(project_dir, "data", "pandas", filename)
        converters = {"image": LoaderUADetrac().image_eval, "vehicle_type": eval, "color": eval, "intersection": eval}
        panda_file = pd.read_csv(full_dir, converters=converters)
        for key in panda_file:
            if "Unnamed" in key:
                continue

        return panda_file

    @staticmethod
    def save(filename, panda_data):
        warnings.warn("deprecated", DeprecationWarning)
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Eva / eva
        csv_folder = os.path.join(project_dir, "data", "pandas")
        if os.path.exists(csv_folder) == False:
            os.makedirs(csv_folder)
        csv_filename = os.path.join(csv_folder, filename)
        panda_data.to_csv(csv_filename, sep=",", index=None)


if __name__ == "__main__":
    loader = LoaderUADetrac()
    images = loader.load_images()
    print("done loading images")
    boxes = loader.load_boxes()
    print("done loading boxes")
    labels = loader.load_labels()
    print("done loading labels")
