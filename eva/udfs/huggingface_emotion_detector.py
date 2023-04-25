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

import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import (
    AutoFeatureExtractor,
    AutoModelForImageClassification,
    DetrForObjectDetection,
    DetrImageProcessor,
)

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF


class HuggingFaceEmotionDetector(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "huggingemotion"

    @staticmethod
    def compute_iou(box1, box2):
        # Compute the coordinates of the intersection rectangle
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        # Compute the area of the intersection rectangle
        intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
        # Compute the area of the union rectangle
        box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
        box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
        union_area = box1_area + box2_area - intersection_area
        # Compute the IoU overlap between the two bounding boxes
        iou = intersection_area / union_area
        return iou

    @staticmethod
    def nms(boxes, scores, iou_threshold):
        # Sort the bounding boxes by their scores in descending order
        sorted_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )
        selected_indices = []
        overlaps = {
            i: {
                j: HuggingFaceEmotionDetector.compute_iou(boxes[i], boxes[j])
                for j in sorted_indices
            }
            for i in sorted_indices
        }
        while sorted_indices:
            # Select the bounding box with the highest score
            i = sorted_indices[0]
            selected_indices.append(i)
            # Remove all the bounding boxes that have an IoU overlap greater than the threshold
            sorted_indices = [
                j for j in sorted_indices[1:] if overlaps[i][j] < iou_threshold
            ]
        # Return the selected bounding boxes
        return [boxes[i] for i in selected_indices]

    def setup(self, threshold=0.85):
        self.threshold = threshold
        face_model = "aditmohan96/detr-finetuned-face"
        emotion_model = "jayanta/google-vit-base-patch16-224-cartoon-emotion-detection"

        self.proc1 = DetrImageProcessor.from_pretrained(face_model)
        self.model1 = DetrForObjectDetection.from_pretrained(face_model)

        self.proc2 = AutoFeatureExtractor.from_pretrained(emotion_model)
        self.model2 = AutoModelForImageClassification.from_pretrained(emotion_model)

    def predict(self, img):
        img = Image.fromarray(img)
        inputs = self.proc1(images=img, return_tensors="pt")
        outputs = self.model1(**inputs)
        target_sizes = torch.tensor([img.size[::-1]])
        faces = self.proc1.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.threshold
        )[0]

        unique_faces = HuggingFaceEmotionDetector.nms(
            faces["boxes"], faces["scores"], 1 - self.threshold
        )
        emotions = []
        confidences = []

        for box in unique_faces:
            box = [int(i) for i in box.tolist()]
            crop_img = img.crop((box[0], box[1], box[2], box[3]))
            features = self.proc2(images=crop_img, return_tensors="pt")
            output = self.model2(**features)

            probs = torch.softmax(output.logits, dim=-1)
            predicted_label = output.logits.argmax(-1).item()

            emotions.append(self.model2.config.id2label[predicted_label])
            confidences.append(probs[0][predicted_label].item())

        return unique_faces, emotions, confidences

    @property
    def labels(self) -> List[str]:
        return ["angry", "happy", "neutral", "sad"]

    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            tuple containing predicted_classes (List[List[str]]),
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])

        """
        frames_list = frames.transpose().values.tolist()[0]
        frames = np.asarray(frames_list)
        outcome = []
        for frame in frames:
            bboxs, emotions, confidences = self.predict(frame)
            outcome.append({"labels": emotions, "scores": confidences, "bboxes": bboxs})
        return pd.DataFrame(outcome, columns=["labels", "scores", "bboxes"])
