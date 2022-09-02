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
import argparse
import functools
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import pkg_resources

# ==============================================
# CONFIGURATION
# ==============================================

# NOTE: absolute path to eva directory is calculated from current directory
# directory structure: eva/scripts/formatting/<this_file>
# EVA_DIR needs to be redefined if the directory structure is changed
CODE_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
EVA_DIR = functools.reduce(
    os.path.join, [CODE_SOURCE_DIR, os.path.pardir, os.path.pardir]
)

# other directory paths used are relative to peloton_dir
EVA_SRC_DIR = os.path.join(EVA_DIR, "eva")
EVA_TEST_DIR = os.path.join(EVA_DIR, "test")
EVA_SCRIPT_DIR = os.path.join(EVA_DIR, "script")

FORMATTING_DIR = os.path.join(EVA_SCRIPT_DIR, "formatting")
PYLINTRC = os.path.join(FORMATTING_DIR, "pylintrc")

# DEFAULT DIRS
DEFAULT_DIRS = []
DEFAULT_DIRS.append(EVA_SRC_DIR)
DEFAULT_DIRS.append(EVA_TEST_DIR)

IGNORE_FILES = [
    "evaql_lexer.py",
    "evaql_parser.py",
    "evaql_parserListener.py",
    "evaql_parserVisitor.py",
]

FLAKE8_VERSION_REQUIRED = "3.9.1"
BLACK_VERSION_REQUIRED = "22.6.0"
ISORT_VERSION_REQUIRED = "5.10.1"

BLACK_BINARY = "black"
FLAKE_BINARY = "flake8"
PYLINT_BINARY = "pylint"
ISORT_BINARY = "isort"

FLAKE8_CONFIG = Path(os.path.join(EVA_DIR, ".flake8")).resolve()
# ==============================================
# HEADER CONFIGURATION
# ==============================================

header = """# coding=utf-8
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
"""

# regular expression used to track header
header_regex = re.compile(r"((\#.*[\n|.])*)", re.M)

# ==============================================
# LOGGING CONFIGURATION
# ==============================================

LOG = logging.getLogger(__name__)
LOG_handler = logging.StreamHandler()
LOG_formatter = logging.Formatter(
    fmt="%(asctime)s [%(funcName)s:%(lineno)03d] %(levelname)-5s: %(message)s",
    datefmt="%m-%d-%Y %H:%M:%S",
)
LOG_handler.setFormatter(LOG_formatter)
LOG.addHandler(LOG_handler)
LOG.setLevel(logging.INFO)

# ==============================================
# UTILITY FUNCTION DEFINITIONS
# ==============================================

# format the file passed as argument


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    # from whichcraft import which
    from shutil import which

    req_version = None
    if name is FLAKE_BINARY:
        req_version = FLAKE8_VERSION_REQUIRED
    elif name is BLACK_BINARY:
        req_version = BLACK_VERSION_REQUIRED
    elif name is ISORT_BINARY:
        req_version = ISORT_VERSION_REQUIRED
    if which(name) is None:
        LOG.error(
            f"{name} is not installed. Install the python package with:"
            f"pip install {name}=={req_version}"
        )
        sys.exit(1)
    else:
        installed_version = pkg_resources.get_distribution(name).version
        if installed_version != req_version:
            LOG.warning(
                f"EVA uses {name} {req_version}. The installed version is"
                f" {installed_version} which can result in different results."
            )


def check_header(file_path):
    abs_path = os.path.abspath(file_path)
    with open(abs_path, "r+") as fd:
        file_data = fd.read()
        header_match = header_regex.match(file_data)
        if header_match is None:
            return False
        header_comment = header_match.group(1)
        if header_comment == header:
            return True
        else:
            return False


def format_file(file_path, add_header, strip_header, format_code):

    abs_path = os.path.abspath(file_path)
    with open(abs_path, "r+") as fd:
        file_data = fd.read()
        if add_header:
            LOG.info("Adding header: " + file_path)
            new_file_data = header + file_data

            fd.seek(0, 0)
            fd.truncate()
            fd.write(new_file_data)

        elif strip_header:
            LOG.info("Stripping headers : " + file_path)
            header_match = header_regex.match(file_data)
            if header_match is None:
                return

            header_comment = header_match.group(1)

            new_file_data = file_data.replace(header_comment, "")

            fd.seek(0, 0)
            fd.truncate()
            fd.write(new_file_data)

        elif format_code:
            LOG.info("Formatting File : " + file_path)
            # ISORT
            isort_command = f"{ISORT_BINARY} --profile  black  {file_path}"
            os.system(isort_command)

            # AUTOPEP
            black_command = f"{BLACK_BINARY}  {file_path}"
            # LOG.info(black_command)
            os.system(black_command)

            # AUTOFLAKE
            autoflake_command = f"{FLAKE_BINARY} --config={FLAKE8_CONFIG} {file_path}"
            ret_val = os.system(autoflake_command)
            if ret_val:
                sys.exit(1)
    # END WITH

    fd.close()


# END FORMAT__FILE(FILE_NAME)


# format all the files in the dir passed as argument
def format_dir(dir_path, add_header, strip_header, format_code):

    for subdir, dir, files in os.walk(dir_path):

        for file in files:
            if file in IGNORE_FILES:
                continue

            file_path = subdir + os.path.sep + file

            if file_path.endswith(".py"):
                format_file(file_path, add_header, strip_header, format_code)
            # END IF
        # END FOR [file]
    # END FOR [os.walk]


# END ADD_HEADERS_DIR(DIR_PATH)

# ==============================================
# Main Function
# ==============================================


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Add/delete headers and/or format source code"
    )

    parser.add_argument(
        "-a",
        "--add-header",
        help="add suitable header(s)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-s",
        "--strip-header",
        help="strip existing header(s)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--format-code",
        help="format modified code",
        action="store_true",
        default=True,
    )
    parser.add_argument("-f", "--file-name", help="file to be acted on")
    parser.add_argument(
        "-d", "--dir-name", help="directory containing files to be acted on"
    )

    args = parser.parse_args()

    # SOME SANITY CHECKS
    if args.add_header and args.strip_header:
        LOG.error("adding & stripping headers cannot be done together")
        sys.exit("adding & stripping headers cannot be done together")

    if args.file_name and args.dir_name:
        LOG.error("file_name and dir_name cannot be specified together")
        sys.exit("file_name and dir_name cannot be specified together")

    # CHECK IF FORMATTERS ARE INSTALLED
    is_tool(BLACK_BINARY)
    is_tool(FLAKE_BINARY)
    is_tool(ISORT_BINARY)
    if args.file_name:
        LOG.info("Scanning file: " + "".join(args.file_name))
        format_file(
            args.file_name,
            args.add_header,
            args.strip_header,
            args.format_code,
        )
    elif args.dir_name:
        LOG.info("Scanning directory " + "".join(args.dir_name))
        format_dir(
            args.dir_name, args.add_header, args.strip_header, args.format_code
        )
    # BY DEFAULT, WE FIX THE MODIFIED FILES
    else:
        # LOG.info("Default fix modified files")
        MERGEBASE = subprocess.check_output(
            "git merge-base origin/master HEAD", shell=True, text=True
        ).rstrip()
        files = (
            subprocess.check_output(
                f"git diff --name-only --diff-filter=ACRM {MERGEBASE} -- '*.py'",
                shell=True,
                text=True,
            )
            .rstrip()
            .split("\n")
        )
        for file in files:
            print(file)
            valid = False
            # only format the defualt directories
            file_path = str(Path(file).absolute())
            for source_dir in DEFAULT_DIRS:
                source_path = str(Path(source_dir).resolve())
                if file_path.startswith(source_path):
                    valid = True

            if valid:
                if not check_header(file):
                    format_file(file, False, True, False)
                    format_file(file, True, False, False)
                format_file(file, False, False, True)