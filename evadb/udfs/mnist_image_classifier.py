# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from collections import OrderedDict

import pandas as pd

from evadb.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from evadb.utils.generic_utils import try_to_import_torch, try_to_import_torchvision


class MnistImageClassifier(PytorchAbstractClassifierUDF):
    @property
    def name(self) -> str:
        return "MnistImageClassifier"

    def setup(self):
        try_to_import_torch()
        try_to_import_torchvision()
        import torch
        import torch.nn as nn

        model_urls = {
            "mnist": "http://ml.cs.tsinghua.edu.cn/~chenxi/pytorch-models/mnist-b07bb66b.pth"  # noqa
        }

        # https://github.com/aaron-xichen/pytorch-playground/blob/master/
        class MLP(nn.Module):
            def __init__(self, input_dims, n_hiddens, n_class):
                super(MLP, self).__init__()
                assert isinstance(input_dims, int), "Please provide int for input_dims"
                self.input_dims = input_dims
                current_dims = input_dims
                layers = OrderedDict()

                if isinstance(n_hiddens, int):
                    n_hiddens = [n_hiddens]
                else:
                    n_hiddens = list(n_hiddens)
                for i, n_hidden in enumerate(n_hiddens):
                    layers["fc{}".format(i + 1)] = nn.Linear(current_dims, n_hidden)
                    layers["relu{}".format(i + 1)] = nn.ReLU()
                    layers["drop{}".format(i + 1)] = nn.Dropout(0.2)
                    current_dims = n_hidden
                layers["out"] = nn.Linear(current_dims, n_class)

                self.model = nn.Sequential(layers)

            def forward(self, input):
                input = input.view(input.size(0), -1)
                assert input.size(1) == self.input_dims
                return self.model.forward(input)

        def mnist(input_dims=784, n_hiddens=[256, 256], n_class=10, pretrained=None):
            model = MLP(input_dims, n_hiddens, n_class)
            import torch.utils.model_zoo as model_zoo

            if pretrained is not None:
                m = model_zoo.load_url(
                    model_urls["mnist"], map_location=torch.device("cpu")
                )
                state_dict = m.state_dict() if isinstance(m, nn.Module) else m
                assert isinstance(state_dict, (dict, OrderedDict)), type(state_dict)
                model.load_state_dict(state_dict)
            return model

        self.model = mnist(pretrained=True)
        self.model.eval()

    @property
    def labels(self):
        return list([str(num) for num in range(10)])

    def transform(self, images):
        from PIL import Image
        from torchvision.transforms import Compose, Grayscale, Normalize, ToTensor

        composed = Compose(
            [
                Grayscale(num_output_channels=1),
                ToTensor(),
                Normalize((0.1307,), (0.3081,)),
            ]
        )
        # reverse the channels from opencv
        return composed(Image.fromarray(images[:, :, ::-1])).unsqueeze(0)

    def forward(self, frames) -> pd.DataFrame:
        outcome = []
        predictions = self.model(frames)
        for prediction in predictions:
            label = self.as_numpy(prediction.data.argmax())
            outcome.append({"label": str(label)})

        return pd.DataFrame(outcome, columns=["label"])
