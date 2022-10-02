import unittest

import numpy as np
import pandas as pd

from eva.udfs.ndarray.array_count import Array_Count


class CropTests(unittest.TestCase):
    def setUp(self):
        self.array_count = Array_Count()

    def test_array_count_name_exists(self):
        assert hasattr(self.array_count, "name")
