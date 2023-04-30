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
from pytest import fixture

from eva.storage.transaction_manager import TransactionManager


# This is a global fixture that will be used by all tests
@fixture(autouse=True)
def wrap_test_in_transaction(request):
    if "notparallel" in request.keywords:
        yield
    else:
        TransactionManager().begin_transaction()
        yield
        TransactionManager().rollback_transaction()
