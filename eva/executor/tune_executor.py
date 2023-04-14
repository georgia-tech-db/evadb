# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from eva.executor.abstract_executor import AbstractExecutor
from eva.plan_nodes.tune_plan import TunePlan
from eva.models.storage.batch import Batch
import pandas as pd
import zipfile
import os
import random
import shutil

class TuneExecutor(AbstractExecutor):
    def __init__(self, node: TunePlan):
        super().__init__(node)

    def exec(self, *args, **kwargs):
        file_name = self.node.file_name
        batch_size = self.node.batch_size
        epochs_size = self.node.epochs_size

        file_path = os.path.join('data', file_name[0].strip("'\""))

        extract_path = os.path.join('data', 'dataset', file_name[0].strip("'\"")[:-4])

        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

        dataset_path = os.path.join(extract_path, 'obj_train_data')

        train_ratio = 0.8
        val_ratio = 0.1
        test_ratio = 0.1

        train_folder = "train"
        val_folder = "valid"
        test_folder = "test"
        image_folder = "images"
        label_folder = "labels"

        folders_to_create = [
            os.path.join(extract_path, image_folder, train_folder),
            os.path.join(extract_path, label_folder, train_folder),
            os.path.join(extract_path, image_folder, val_folder),
            os.path.join(extract_path, label_folder, val_folder),
            os.path.join(extract_path, image_folder, test_folder),
            os.path.join(extract_path, label_folder, test_folder),
        ]

        for folder in folders_to_create:
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        image_files = [f for f in os.listdir(dataset_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        num_images = len(image_files)
        num_train = int(num_images * train_ratio)
        num_val = int(num_images * val_ratio)
        num_test = num_images - num_train - num_val

        random.shuffle(image_files)

        for i, image_file in enumerate(image_files):
            if i < num_train:
                target_image_folder = os.path.join(extract_path, image_folder, train_folder)
                target_label_folder = os.path.join(extract_path, label_folder, train_folder)
            elif i < num_train + num_val:
                target_image_folder = os.path.join(extract_path, image_folder, val_folder)
                target_label_folder = os.path.join(extract_path, label_folder, val_folder)
            else:
                target_image_folder = os.path.join(extract_path, image_folder, test_folder)
                target_label_folder = os.path.join(extract_path, label_folder, test_folder)

            target_image_file = os.path.join(target_image_folder, image_file)
            target_label_file = os.path.join(target_label_folder, image_file[:-4] + ".txt")

            if not os.path.exists(target_image_file):
                shutil.copy(os.path.join(dataset_path, image_file), target_image_folder)

            if not os.path.exists(target_label_file):
                shutil.copy(os.path.join(dataset_path, image_file[:-4] + ".txt"), target_label_folder)

        testing = {"dataset": [file_path], "batch_size": [batch_size], "epochs_size": [epochs_size], 
                    "num_images": [num_images], "num_train": [num_train], "num_val": [num_val], "num_test": [num_test]}

        yield Batch(pd.DataFrame(testing))
