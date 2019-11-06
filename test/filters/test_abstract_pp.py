import unittest
import numpy as np
from src.filters.abstract_pp import abstract_PP_filter_template
from src.query_executor.pp_executor import PpExecutor
from src.models import FrameBatch, Frame, Prediction, Predicate
from src.filters.minimum_filter import FilterMinimum
from unittest import mock
from src.filters.abstract_pp import abstract_PP_filter_template
class abstract_ppTest(unittest.TestCase):


    @mock.patch.object(abstract_PP_filter_template, '_init_model')
    def test_mocking_instance(self, mocked_instance):
        dummy = type("dummymodel", (), {"predict": lambda x: [True, True, False]})
        mocked_instance.return_value = dummy
        a = abstract_PP_filter_template("blabla")

        frame_1 = Frame(1, np.ones((1,1)), None)
        frame_2 = Frame(1, 2 * np.ones((1,1)), None)
        frame_3 = Frame(1, 3 * np.ones(((1, 1))), None)
        batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)
        self.assertEqual(a.predict(batch), FrameBatch(frames=[frame_1, frame_2], info=None))
