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
from pathlib import Path

from evadb.binder.binder_utils import (
    BinderError,
    extend_star,
    resolve_alias_table_value_expression,
)
from evadb.binder.statement_binder import StatementBinder
from evadb.catalog.catalog_utils import (
    get_metadata_properties,
    get_video_table_column_definitions,
)
from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.executor.execution_context import Context
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.types import FunctionType
from evadb.third_party.huggingface.binder import assign_hf_function
from evadb.utils.generic_utils import (
    load_function_class_from_file,
    string_comparison_case_insensitive,
)
from evadb.utils.logging_manager import logger


def bind_func_expr(binder: StatementBinder, node: FunctionExpression):
    # setup the context
    # we read the GPUs from the catalog and populate in the context
    gpus_ids = binder._catalog().get_configuration_catalog_value("gpu_ids")
    node._context = Context(gpus_ids)

    # handle the special case of "extract_object"
    if node.name.upper() == str(FunctionType.EXTRACT_OBJECT):
        handle_bind_extract_object_function(node, binder)
        return

    # Handle Func(*)
    if (
        len(node.children) == 1
        and isinstance(node.children[0], TupleValueExpression)
        and node.children[0].name == "*"
    ):
        node.children = extend_star(binder._binder_context)
    # bind all the children
    for child in node.children:
        binder.bind(child)

    function_obj = binder._catalog().get_function_catalog_entry_by_name(node.name)
    if function_obj is None:
        err_msg = (
            f"Function '{node.name}' does not exist in the catalog. "
            "Please create the function using CREATE FUNCTION command."
        )
        logger.error(err_msg)
        raise BinderError(err_msg)

    if string_comparison_case_insensitive(function_obj.type, "HuggingFace"):
        node.function = assign_hf_function(function_obj)

    elif string_comparison_case_insensitive(function_obj.type, "Ludwig"):
        function_class = load_function_class_from_file(
            function_obj.impl_file_path,
            "GenericLudwigModel",
        )
        function_metadata = get_metadata_properties(function_obj)
        assert "model_path" in function_metadata, "Ludwig models expect 'model_path'."
        node.function = lambda: function_class(
            model_path=function_metadata["model_path"]
        )

    else:
        if function_obj.type == "ultralytics":
            # manually set the impl_path for yolo functions we only handle object
            # detection for now, hopefully this can be generalized
            function_dir = Path(EvaDB_INSTALLATION_DIR) / "functions"
            function_obj.impl_file_path = (
                Path(f"{function_dir}/yolo_object_detector.py").absolute().as_posix()
            )

        # Verify the consistency of the function. If the checksum of the function does not
        # match the one stored in the catalog, an error will be thrown and the user
        # will be asked to register the function again.
        # assert (
        #     get_file_checksum(function_obj.impl_file_path) == function_obj.checksum
        # ), f"""Function file {function_obj.impl_file_path} has been modified from the
        #     registration. Please use DROP FUNCTION to drop it and re-create it # using CREATE FUNCTION."""

        try:
            function_class = load_function_class_from_file(
                function_obj.impl_file_path,
                function_obj.name,
            )
            # certain functions take additional inputs like yolo needs the model_name
            # these arguments are passed by the user as part of metadata
            # we also handle the special case of ChatGPT where we need to send the
            # OpenAPI key as part of the parameter if not provided by the user
            properties = get_metadata_properties(function_obj)
            if string_comparison_case_insensitive(node.name, "CHATGPT"):
                # if the user didn't provide any API_KEY, check if we have one in the catalog
                if "OPENAI_API_KEY" not in properties.keys():
                    openai_key = binder._catalog().get_configuration_catalog_value(
                        "OPENAI_API_KEY"
                    )
                    properties["openai_api_key"] = openai_key

            node.function = lambda: function_class(**properties)
        except Exception as e:
            err_msg = (
                f"{str(e)}. Please verify that the function class name in the "
                "implementation file matches the function name."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

    node.function_obj = function_obj
    output_objs = binder._catalog().get_function_io_catalog_output_entries(function_obj)
    if node.output:
        for obj in output_objs:
            if obj.name.lower() == node.output:
                node.output_objs = [obj]
        if not node.output_objs:
            err_msg = f"Output {node.output} does not exist for {function_obj.name}."
            logger.error(err_msg)
            raise BinderError(err_msg)
        node.projection_columns = [node.output]
    else:
        node.output_objs = output_objs
        node.projection_columns = [obj.name.lower() for obj in output_objs]

    resolve_alias_table_value_expression(node)


def handle_bind_extract_object_function(
    node: FunctionExpression, binder_context: StatementBinder
):
    """Handles the binding of extract_object function.
        1. Bind the source video data
        2. Create and bind the detector function expression using the provided name.
        3. Create and bind the tracker function expression.
            Its inputs are id, data, output of detector.
        4. Bind the EXTRACT_OBJECT function expression and append the new children.
        5. Handle the alias and populate the outputs of the EXTRACT_OBJECT function
    Args:
        node (FunctionExpression): The function expression representing the extract object operation.
        binder_context (StatementBinder): The binder object used to bind expressions in the statement.
    Raises:
        AssertionError: If the number of children in the `node` is not equal to 3.
    """
    assert (
        len(node.children) == 3
    ), f"Invalid arguments provided to {node}. Example correct usage, (data, Detector, Tracker)"

    # 1. Bind the source video
    video_data = node.children[0]
    binder_context.bind(video_data)

    # 2. Construct the detector
    # convert detector to FunctionExpression before binding
    # eg. YoloV5 -> YoloV5(data)
    detector = FunctionExpression(None, node.children[1].name)
    detector.append_child(video_data.copy())
    binder_context.bind(detector)

    # 3. Construct the tracker
    # convert tracker to FunctionExpression before binding
    # eg. ByteTracker -> ByteTracker(id, data, labels, bboxes, scores)
    tracker = FunctionExpression(None, node.children[2].name)
    # create the video id expression
    columns = get_video_table_column_definitions()
    tracker.append_child(
        TupleValueExpression(name=columns[1].name, table_alias=video_data.table_alias)
    )
    tracker.append_child(video_data.copy())
    binder_context.bind(tracker)
    # append the bound output of detector
    for obj in detector.output_objs:
        col_alias = "{}.{}".format(obj.function_name.lower(), obj.name.lower())
        child = TupleValueExpression(
            obj.name,
            table_alias=obj.function_name.lower(),
            col_object=obj,
            col_alias=col_alias,
        )
        tracker.append_child(child)

    # 4. Bind the EXTRACT_OBJECT expression and append the new children.
    node.children = []
    node.children = [video_data, detector, tracker]

    # 5. assign the outputs of tracker to the output of extract_object
    node.output_objs = tracker.output_objs
    node.projection_columns = [obj.name.lower() for obj in node.output_objs]

    # 5. resolve alias based on the what user provided
    # we assign the alias to tracker as it governs the output of the extract object
    resolve_alias_table_value_expression(node)
    tracker.alias = node.alias
