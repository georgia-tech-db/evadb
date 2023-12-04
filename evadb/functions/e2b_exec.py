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

import json

import pandas as pd
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction, InputType
from evadb.functions.decorators.decorators import setup, forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from e2b import Sandbox


class E2BExec(AbstractFunction):
    """
    Takes input as a string like:
    {
       "function_call":{
          "name":"exec_code",
          "arguments":"{\n  \"code\": \"def fibonacci(n):\\n    fibonacci_sequence = [0, 1]\\n    while len(fibonacci_sequence) < n:\\n        fibonacci_sequence.append(fibonacci_sequence[-1] + fibonacci_sequence[-2])\\n    return fibonacci_sequence\\n\\nprint(fibonacci(100))\"\n}"
       }
    }
    This is the output from OpenAI Chat Completion model.
    """
    @setup(cacheable=False, function_type="code_execution", batchable=True)
    def setup(self, *args, **kwargs) -> None:
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["stdout", "stderr"],
                column_types=[NdArrayType.STR, ],
                column_shapes=[(1,), (1, )],
            )
        ],
    )
    def forward(self, frames: InputType) -> InputType:
        self.sandbox = Sandbox()
        output = []
        stderrs = []
        for code in frames['codejson']:
            code_obj = json.loads(code)
            code_text = json.loads(code_obj['function_call']['arguments'])['code']
            self.sandbox.filesystem.write('/home/user/test.py', code_text)
            proc = self.sandbox.process.start('python /home/user/test.py')
            out = proc.wait()
            output.append(out.stdout)
            stderrs.append(out.stderr)

        return_df = pd.DataFrame({"stdout": output, "stderr": stderrs})
        self.sandbox.close()
        return return_df

    @property
    def name(self) -> str:
        return 'E2BExec'
