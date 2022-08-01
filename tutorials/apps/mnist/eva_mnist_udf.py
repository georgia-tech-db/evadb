import pandas as pd
from torch import Tensor
import torch
from eva.udfs.pytorch_abstract_udf import PytorchAbstractUDF
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from torchvision.transforms import Compose, ToTensor, Normalize, Grayscale


class MnistCNN(PytorchAbstractUDF):

    @property
    def name(self) -> str:
        return 'MnistCNN'

    def __init__(self):
        super().__init__()
        self.model = mnist(pretrained=True)
        self.model.eval()

    @property
    def input_format(self):
        return FrameInfo(1, 28, 28, ColorSpace.RGB)

    @property
    def labels(self):
        return list([str(num) for num in range(10)])

    @property
    def transforms(self) -> Compose:
        return Compose([
            Grayscale(num_output_channels=1),
            ToTensor(),
            Normalize((0.1307,), (0.3081,))
        ])

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        outcome = pd.DataFrame()
        predictions = self.model(frames)
        for prediction in predictions:
            label = self.as_numpy(prediction.data.argmax())
            outcome = outcome.append({"label" : str(label)}, ignore_index=True)
        
        return outcome



import torch.nn as nn
from collections import OrderedDict
import torch.utils.model_zoo as model_zoo

model_urls = {
    'mnist': 'http://ml.cs.tsinghua.edu.cn/~chenxi/pytorch-models/mnist-b07bb66b.pth'  # noqa
}


# https://github.com/aaron-xichen/pytorch-playground/blob/master/
class MLP(nn.Module):
    def __init__(self, input_dims, n_hiddens, n_class):
        super(MLP, self).__init__()
        assert isinstance(input_dims, int), 'Please provide int for input_dims'
        self.input_dims = input_dims
        current_dims = input_dims
        layers = OrderedDict()

        if isinstance(n_hiddens, int):
            n_hiddens = [n_hiddens]
        else:
            n_hiddens = list(n_hiddens)
        for i, n_hidden in enumerate(n_hiddens):
            layers['fc{}'.format(i + 1)] = nn.Linear(current_dims, n_hidden)
            layers['relu{}'.format(i + 1)] = nn.ReLU()
            layers['drop{}'.format(i + 1)] = nn.Dropout(0.2)
            current_dims = n_hidden
        layers['out'] = nn.Linear(current_dims, n_class)

        self.model = nn.Sequential(layers)

    def forward(self, input):
        input = input.view(input.size(0), -1)
        assert input.size(1) == self.input_dims
        return self.model.forward(input)


def mnist(input_dims=784, n_hiddens=[256, 256], n_class=10, pretrained=None):
    model = MLP(input_dims, n_hiddens, n_class)
    if pretrained is not None:
        m = model_zoo.load_url(model_urls['mnist'], map_location=torch.device('cpu'))
        state_dict = m.state_dict() if isinstance(m, nn.Module) else m
        assert isinstance(state_dict, (dict, OrderedDict)), type(state_dict)
        model.load_state_dict(state_dict)
    return model