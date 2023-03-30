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
import os
from typing import List

import torch
from eva.udfs.utils import *
from numpy import array
from eva.udfs.darknet import Darknet
from torch.autograd import Variable
from torch.cuda import is_available as check_cuda
from PIL.ImageOps import grayscale
from fastai.vision.all import PILImage, load_learner
import cv2
import pandas as pd


from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF


class HuggingFaceEmotionDetector(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "huggingemotion"

    def getFile(self, url, file):
        print(os.getcwd())
        if (not os.path.isfile(file)):
            response = requests.get(url)
            with open(file, 'wb') as f:
                f.write(response.content)

    def setup(self, threshold=0.85):
        self.threshold = threshold
        self.batch_size = 1
        self.confidence = 0.25
        self.nms_thresh = 0.30
        run_cuda = False

        # CFG Files
        cfg_url = 'https://huggingface.co/spaces/schibsted/Facial_Recognition_with_Sentiment_Detector/resolve/main/cfg/yolov3-openimages.cfg'
        cfg_file = 'yolov3-openimages.cfg'
        clsnames_url = 'https://huggingface.co/spaces/schibsted/Facial_Recognition_with_Sentiment_Detector/resolve/main/cfg/openimages.names'
        clsnames_file = 'openimages.names'
        weights_url = 'https://huggingface.co/spaces/schibsted/Facial_Recognition_with_Sentiment_Detector/resolve/main/cfg/yolov3-openimages.weights'
        weights_file = 'yolov3-openimages.weights'

        self.getFile(cfg_url ,cfg_file)
        self.getFile(clsnames_url ,clsnames_file)
        self.getFile(weights_url ,weights_file)


        self.classes = load_classes(clsnames_file)
        self.num_classes = len(self.classes)

        # Set up the neural network
        self.model = Darknet( cfg_file)

        print('Load Weights')
        self.model.load_weights(weights_file)

        self.CUDA = False

        print('Successfully loaded Network')

        self.inp_dim = int(self.model.net_info["height"])
        self.model.eval()

        # Emotion
        emotion_model_weights_url = 'https://huggingface.co/spaces/schibsted/Facial_Recognition_with_Sentiment_Detector/resolve/main/models/emotions_vgg19.pkl'
        emotion_model_weights = 'emotions_vgg19.pkl'
        self.getFile(emotion_model_weights_url, emotion_model_weights)
        self.learn_emotion = load_learner(emotion_model_weights)
        self.learn_emotion_labels = self.learn_emotion.dls.vocab

    def get_detections(self, x):
        c1 = [int(y) for y in x[1:3]]
        c2 = [int(y) for y in x[3:5]]

        det_class = int(x[-1])
        label = "{0}".format(self.classes[det_class])

        return (label, tuple(c1 + c2))

    def detector(self, image):
        # Just lazy to update this
        imlist = [image]
        loaded_ims = [image]

        im_batches = list(map(prep_image, loaded_ims, [self.inp_dim for x in range(len(imlist))]))
        im_dim_list = [(x.shape[1], x.shape[0]) for x in loaded_ims]
        im_dim_list = torch.FloatTensor(im_dim_list).repeat(1, 2)

        leftover = 0
        if (len(im_dim_list) % self.batch_size):
            leftover = 1

        if self.batch_size != 1:
            num_batches = len(imlist) // self.batch_size + leftover
            im_batches = [torch.cat((im_batches[i * self.batch_size: min((i + 1) * self.batch_size,
                                                                    len(im_batches))])) for i in range(num_batches)]

        write = 0
        if self.CUDA:
            im_dim_list = im_dim_list.cuda()

        for i, batch in enumerate(im_batches):
            # load the image

            if self.CUDA:
                batch = batch.cuda()
            with torch.no_grad():
                prediction = self.model(Variable(batch), self.CUDA)

            prediction = write_results(prediction, self.confidence, self.num_classes, nms_conf=self.nms_thresh)

            if type(prediction) == int:

                for im_num, image in enumerate(imlist[i * self.batch_size: min((i + 1) * self.batch_size, len(imlist))]):
                    im_id = i * self.batch_size + im_num

                continue

            prediction[:, 0] += i * self.batch_size  # transform the atribute from index in batch to index in imlist

            if not write:  # If we have't initialised output
                output = prediction
                write = 1
            else:
                output = torch.cat((output, prediction))

            for im_num, image in enumerate(imlist[i * self.batch_size: min((i + 1) * self.batch_size, len(imlist))]):
                im_id = i * self.batch_size + im_num
                objs = [self.classes[int(x[-1])] for x in output if int(x[0]) == im_id]

            if self.CUDA:
                torch.cuda.synchronize()

        try:
            output
        except NameError:
            return loaded_ims[0], []

        im_dim_list = torch.index_select(im_dim_list, 0, output[:, 0].long())

        scaling_factor = torch.min(608 / im_dim_list, 1)[0].view(-1, 1)

        output[:, [1, 3]] -= (self.inp_dim - scaling_factor * im_dim_list[:, 0].view(-1, 1)) / 2
        output[:, [2, 4]] -= (self.inp_dim - scaling_factor * im_dim_list[:, 1].view(-1, 1)) / 2

        output[:, 1:5] /= scaling_factor

        for i in range(output.shape[0]):
            output[i, [1, 3]] = torch.clamp(output[i, [1, 3]], 0.0, im_dim_list[i, 0])
            output[i, [2, 4]] = torch.clamp(output[i, [2, 4]], 0.0, im_dim_list[i, 1])

        detections = list(map(self.get_detections, output))

        if self.CUDA:
            torch.cuda.empty_cache()

        return loaded_ims[0], detections

    def crop_images(self, img, bbox):
        # Coordinates of face in cv2 format
        xmin, ymin, xmax, ymax = bbox[1]

        # resize and crop face
        return img.crop((xmin, ymin, xmax, ymax))

    def detect_person_face(self, img, detections):
        '''This function is called from within detect face.
        If only a person is detected, then this will crop
        image and then try to detect face again.'''

        faces = []
        boxes = []

        # Loop through people
        for detection in detections:

            # Get cropped image of person
            temp = self.crop_images(img, detection)

            # run detector again
            _, detect = self.detector(array(temp))

            # check for human faces
            human_face = [idx for idx, val in enumerate(detect) if val[0] == 'Human face']

            if len(human_face) == 0:
                continue

            # Force it to take only 1 face per person
            # crop face and append to list
            faces.append(self.crop_images(temp, detect[human_face[0]]))
            boxes.append(detect[human_face[0]])

        return faces, boxes

    def detect_face(self, img):

        _, detections = self.detector(array(img))

        # check for human faces
        human_face = [idx for idx, val in enumerate(detections) if val[0] == 'Human face']

        if len(human_face) == 0:
            human_face = [idx for idx, val in enumerate(detections) if val[0] == 'Person']

            if len(human_face) == 0:
                return []
            else:
                # Only get human face detections
                faces, boxes = self.detect_person_face(img, [detections[idx] for idx in human_face])

        else:
            # Only get human face detections
            faces = []
            boxes = []

            for idx in human_face:
                faces.append(self.crop_images(img, detections[idx]))
                boxes.append(detections[idx])

        return faces, boxes

    def predict(self, img):

        org_img = img
        img = PILImage.create(img)

        # Detect faces
        faces, detections = self.detect_face(img)

        bboxes=[]
        emotions=[]
        confidences=[]

        for i in range(len(faces)):

            img = faces[i].resize((48, 48))

            pred_emotion, pred_emotion_idx, probs_emotion = self.learn_emotion.predict(array(grayscale(img)))

            emotion = "Null"
            confidence = 0

            for j in range(len(self.learn_emotion_labels)):
                if (probs_emotion[j] > confidence):
                    confidence = probs_emotion[j]
                    emotion = self.learn_emotion_labels[j]

            x1, y1, x2, y2 = detections[i][1]
            bboxes.append(detections[i][1])
            emotions.append(emotion)
            confidences.append(confidence)

        return bboxes, emotions, confidences

    @property
    def labels(self) -> List[str]:
        return [
            "Angry",
            "Disgust",
            "Fear",
            "Happy",
            "Sad",
            "Surprise",
            "Neutral"
        ]

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
            valid_pred = [confidences.index(x) for x in confidences if x > self.threshold]

            if valid_pred:
                pred_t = valid_pred[-1]
            else:
                pred_t = -1

            bboxs = np.array(bboxs[: pred_t + 1])
            emotions = np.array(emotions[: pred_t + 1])
            confidences = np.array(confidences[: pred_t + 1])
            outcome.append(
                {"labels": emotions, "scores": confidences, "bboxes": bboxs}
            )
        return pd.DataFrame(outcome, columns=["labels", "scores", "bboxes"])
