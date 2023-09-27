from pathlib import Path

from evadb.binder.binder_utils import (
    BinderError,
    extend_star,
    handle_bind_extract_object_function,
    resolve_alias_table_value_expression,
)
from evadb.catalog.catalog_utils import get_metadata_properties
from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.types import FunctionType
from evadb.third_party.huggingface.binder import assign_hf_function
from evadb.utils.generic_utils import (
    load_function_class_from_file,
    string_comparison_case_insensitive,
)
from evadb.utils.logging_manager import logger
from evadb.binder.statement_binder import StatementBinder
from evadb.expression.function_expression import FunctionExpression


def bind_function_expression(binder: StatementBinder, node: FunctionExpression):
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
        assert (
            "model_path" in function_metadata
        ), "Ludwig models expect 'model_path'."
        node.function = lambda: function_class(
            model_path=function_metadata["model_path"]
        )

    else:
        if function_obj.type == "ultralytics":
            # manually set the impl_path for yolo functions we only handle object
            # detection for now, hopefully this can be generalized
            function_dir = Path(EvaDB_INSTALLATION_DIR) / "functions"
            function_obj.impl_file_path = (
                Path(f"{function_dir}/yolo_object_detector.py")
                .absolute()
                .as_posix()
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
            node.function = lambda: function_class(
                **get_metadata_properties(function_obj)
            )
        except Exception as e:
            err_msg = (
                f"{str(e)}. Please verify that the function class name in the "
                "implementation file matches the function name."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

    # TODO: for now, we only check the validity of tuple value expression. 
    # We can extend this validity checking later. Here are some limitations that 
    # we currently face:
    # 1. We cannot really check name for constant value expression. 
    # 2. We should be able to check chained function expression based their output
    #    and inputs, but it will introduce many breaking changes for the test suite.
    should_check_func_input = True
    for child in node.children:
        if not isinstance(child, TupleValueExpression):
            should_check_func_input = False

    if should_check_func_input:
        for arg in function_obj.args:
            col_name = arg.name
            found_valid_col = False
            for alias, _ in binder._binder_context._table_alias_map.items():
                if binder._binder_context._check_table_alias_map(alias, col_name) is not None:
                    found_valid_col = True
            if not found_valid_col:
                raise BinderError(f"Function {function_obj.name} input column '{col_name}' cannot be resolved.")
        
    node.function_obj = function_obj
    output_objs = binder._catalog().get_function_io_catalog_output_entries(
        function_obj
    )
    if node.output:
        for obj in output_objs:
            if obj.name.lower() == node.output:
                node.output_objs = [obj]
        if not node.output_objs:
            err_msg = (
                f"Output {node.output} does not exist for {function_obj.name}."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)
        node.projection_columns = [node.output]
    else:
        node.output_objs = output_objs
        node.projection_columns = [obj.name.lower() for obj in output_objs]

    resolve_alias_table_value_expression(node)
