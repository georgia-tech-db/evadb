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
from typing import List

from eva.catalog.models.udf_catalog import UdfCatalogEntry
from eva.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry
from eva.catalog.catalog_utils import get_metadata_entry_or_val
from eva.udfs.yolo_object_detector import Yolo


def assign_yolo_udf(udf_obj: UdfCatalogEntry):
    """
    Assigns the correct yolo model to the UDF. The model is provided as part of the metadata
    """

    model = get_metadata_entry_or_val(udf_obj, "model", "yolov8m.pt")[1]
    return lambda: Yolo(model)


def parse_yolo_args(metadata_list: List[UdfMetadataCatalogEntry]):
    """
    Parse the metadata information associated with yolo and it as dictionary
    """
    model = "yolov8m.pt"
    for metadata in metadata_list:
        model = get_metadata_entry_or_val(metadata, "model", "yolov8m.pt")

    return {"model_name": model}
