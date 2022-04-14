# coding=utf-8
# Copyright 2018-2020 EVA
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

# ==============================================
# GOAL : Format code, Add/Strip headers
# ==============================================

import argparse
import logging
import os
import re
import sys
import functools

# ==============================================
# CONFIGURATION
# ==============================================

# NOTE: absolute path to eva directory is calculated from current directory
# directory structure: eva/scripts/formatting/<this_file>
# EVA_DIR needs to be redefined if the directory structure is changed
CODE_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
EVA_DIR = functools.reduce(os.path.join,
                           [CODE_SOURCE_DIR, os.path.pardir, os.path.pardir])

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

AUTOPEP_BINARY = "autopep8"
AUTOFLAKE_BINARY = "autoflake"
PYLINT_BINARY = "pylint"

# ==============================================
# HEADER CONFIGURATION
# ==============================================

header = """# coding=utf-8
# Copyright 2018-2020 EVA
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
    fmt='%(asctime)s [%(funcName)s:%(lineno)03d] %(levelname)-5s: %(message)s',
    datefmt='%m-%d-%Y %H:%M:%S'
)
LOG_handler.setFormatter(LOG_formatter)
LOG.addHandler(LOG_handler)
LOG.setLevel(logging.INFO)

# ==============================================
# UTILITY FUNCTION DEFINITIONS
# ==============================================

# format the file passed as argument


def format_file(file_path, add_header, strip_header, format_code):

    abs_path = os.path.abspath(file_path)
    LOG.info(file_path)

    with open(abs_path, "r+") as fd:
        file_data = fd.read()

        if add_header:
            new_file_data = header + file_data

            fd.seek(0, 0)
            fd.truncate()
            fd.write(new_file_data)

        elif strip_header:

            header_match = header_regex.match(file_data)
            if header_match is None:
                return

            header_comment = header_match.group(1)

            new_file_data = file_data.replace(header_comment, "")

            fd.seek(0, 0)
            fd.truncate()
            fd.write(new_file_data)

        elif format_code:

            # AUTOPEP
            autopep_command = AUTOPEP_BINARY + \
                " --in-place --aggressive " + file_path
            # LOG.info(autopep_command)
            os.system(autopep_command)

            # AUTOFLAKE
            autoflake_command = AUTOFLAKE_BINARY + \
                " --in-place --remove-all-unused-imports"\
                " --remove-unused-variables " + file_path
            # LOG.info(autoflake_command)
            os.system(autoflake_command)

            # PYLINT
            pylint_command = PYLINT_BINARY + \
                " --rcfile=" + PYLINTRC + " " + file_path
            # LOG.info(pylint_command)
            # os.system(pylint_command)

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Add/delete headers and/or format source code')

    parser.add_argument("-a", "--add-header", help='add suitable header(s)',
                        action='store_true', default=False)
    parser.add_argument("-s", "--strip-header", help='strip existing header(s)',
                        action='store_true', default=False)
    parser.add_argument("-c", "--format-code", help='format code',
                        action='store_true', default=True)
    parser.add_argument("-f", "--file-name",
                        help='file to be acted on')
    parser.add_argument("-d", "--dir-name",
                        help='directory containing files to be acted on')

    args = parser.parse_args()

    # SOME SANITY CHECKS
    if args.add_header and args.strip_header:
        LOG.error("adding & stripping headers cannot be done together")
        sys.exit("adding & stripping headers cannot be done together")
    if args.file_name and args.dir_name:
        LOG.error("file_name and dir_name cannot be specified together")
        sys.exit("file_name and dir_name cannot be specified together")

    if args.file_name:
        LOG.info("Scanning file: " + ''.join(args.file_name))
        format_file(args.file_name, args.add_header,
                    args.strip_header,
                    args.format_code)
    elif args.dir_name:
        LOG.info("Scanning directory " + ''.join(args.dir_name))
        format_dir(args.dir_name,
                   args.add_header,
                   args.strip_header,
                   args.format_code)
    # BY DEFAULT, WE SCAN THE DEFAULT DIRS AND FIX THEM
    else:
        LOG.info("Default scan")
        for dir in DEFAULT_DIRS:
            LOG.info("Scanning : " + dir + "\n\n")

            LOG.info("Stripping headers : " + dir)
            args.add_header = False
            args.strip_header = True
            args.format_code = False
            format_dir(dir,
                       args.add_header,
                       args.strip_header,
                       args.format_code)

            LOG.info("Adding headers : " + dir)
            args.add_header = True
            args.strip_header = False
            args.format_code = False
            format_dir(dir,
                       args.add_header,
                       args.strip_header,
                       args.format_code)

            LOG.info("Formatting code : " + dir)
            args.add_header = False
            args.strip_header = False
            args.format_code = True
            format_dir(dir,
                       args.add_header,
                       args.strip_header,
                       args.format_code)
