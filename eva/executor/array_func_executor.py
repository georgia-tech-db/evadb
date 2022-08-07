# # coding=utf-8
# # Copyright 2018-2022 EVA
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# from eva.binder.binder_utils import create_table_metadata, handle_if_not_exists
# from eva.executor.abstract_executor import AbstractExecutor
# from eva.executor.executor_utils import ExecutorError
# from eva.planner.create_plan import CreatePlan
# from eva.utils.logging_manager import logger


# class ArrayFunctionExecutor(AbstractExecutor):
#     def __init__(self, node: ArrayPlan):
#         super().__init__(node)

#     def validate(self):
#         pass

#     def exec(self):
#         if node.array_func == ArrayFunctions.Unnest:
#             self._unnest()

#     # Array function definitions
#     def _unnest(self):
#         done_with_iteration = False
#         child_executor = self.children[0]
#         for batch in child_executor.exec():
#             if not done_with_iteration:
#                 # only check in the first iteration
#                 if len(batch.columns) != len(self.node.columns):
#                     err_msg = f"Expected {len(self.node.columns)} columns, got {len(batch.columns)} columns"
#                     logger.error(err_msg)
#                     raise ExecutorError(err_msg)
            
#             for col in batch.columns:
#                 batch.project(col)
