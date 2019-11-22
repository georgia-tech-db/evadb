import unittest
from unittest import mock

import numpy as np

from src.filters.abstract_pp import AbstractPPTemplate
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class AbstractPPTest(unittest.TestCase):

    @mock.patch.object(AbstractPPTemplate, '_init_model')
    def test_mocking_instance(self, mocked_instance):
        dummy = type("dummymodel", (),
                     {"predict": lambda x: [True, True, False]})
        mocked_instance.return_value = dummy
        a = AbstractPPTemplate("blabla")

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(1, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(1, 3 * np.ones(((1, 1))), None)
        batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)
        self.assertEqual(a.predict(batch),
                         FrameBatch(frames=[frame_1, frame_2], info=None))
