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

import os
import sys

import pytest

asyncio_skip_marker = pytest.mark.skipif(
    sys.version_info < (3, 8), reason="Test case requires asyncio support"
)

windows_skip_marker = pytest.mark.skipif(
    sys.platform == "win32", reason="Test case not supported on Windows"
)

linux_skip_marker = pytest.mark.skipif(
    sys.platform == "linux", reason="Test case not supported on Linux"
)

memory_skip_marker = pytest.mark.skipif(
    sys.platform == "linux", reason="Test case consumes too much memory"
)

ray_skip_marker = pytest.mark.skipif(
    os.environ.get("ray") is None,
    reason="Skip test for ray execution.",
)

ray_only_marker = pytest.mark.skipif(
    os.environ.get("ray") is not None,
    reason="Run only if ray is enabled",
)

duplicate_skip_marker = pytest.mark.skipif(
    sys.platform == "linux",
    reason="Test case is duplicate. Disabling to speed up test suite",
)

ocr_skip_marker = pytest.mark.skipif(
    sys.platform == "linux",
    reason="We do not have built-in support for OCR",
)
