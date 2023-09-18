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
import argparse
import functools
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
import asyncio
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path

import pkg_resources

background_loop = asyncio.new_event_loop()

def background(f):
    def wrapped(*args, **kwargs):
        return background_loop.run_in_executor(None, f, *args, **kwargs)

    return wrapped

# ==============================================
# CONFIGURATION
# ==============================================

# NOTE: absolute path to repo directory is calculated from current directory
# directory structure: evadb/scripts/formatting/<this_file>
# EvaDB_DIR needs to be redefined if the directory structure is changed
CODE_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
EvaDB_DIR = functools.reduce(
    os.path.join, [CODE_SOURCE_DIR, os.path.pardir, os.path.pardir]
)

# other directory paths used are relative to root_dir
EvaDB_SRC_DIR = os.path.join(EvaDB_DIR, "evadb")
EvaDB_TEST_DIR = os.path.join(EvaDB_DIR, "test")
EvaDB_SCRIPT_DIR = os.path.join(EvaDB_DIR, "script")
EvaDB_NOTEBOOKS_DIR = os.path.join(EvaDB_DIR, "tutorials")
EvaDB_DOCS_DIR = os.path.join(EvaDB_DIR, "docs")
EvaDB_APPS_DIR = os.path.join(EvaDB_DIR, "apps")

FORMATTING_DIR = os.path.join(EvaDB_SCRIPT_DIR, "formatting")
PYLINTRC = os.path.join(FORMATTING_DIR, "pylintrc")

# DEFAULT DIRS
DEFAULT_DIRS = []
DEFAULT_DIRS.append(EvaDB_SRC_DIR)
DEFAULT_DIRS.append(EvaDB_TEST_DIR)
DEFAULT_DIRS.append(EvaDB_APPS_DIR)

IGNORE_FILES = ["version.py"]
IGNORE_PRINT_FILES = [
    "apps/privategpt/privateGPT.py",
    "apps/privategpt/ingest.py",
    "apps/story_qa/evadb_qa.py",
    "apps/youtube_qa/youtube_qa.py",
    "apps/youtube_channel_qa/youtube_channel_qa.py",
]

FLAKE8_VERSION_REQUIRED = "3.9.1"
BLACK_VERSION_REQUIRED = "22.6.0"
ISORT_VERSION_REQUIRED = "5.10.1"

BLACK_BINARY = "black"
FLAKE_BINARY = "flake8"
ISORT_BINARY = "isort"
PYLINT_BINARY = "pylint"

FLAKE8_CONFIG = Path(os.path.join(EvaDB_DIR, ".flake8")).resolve()

# IGNORED WORDS -- script/formatting/spelling.txt
ignored_words_file = Path(os.path.join(FORMATTING_DIR, "spelling.txt")).resolve()
with open(ignored_words_file) as f:
    ignored_words = [word.strip() for word in f]

# ==============================================
# HEADER CONFIGURATION
# ==============================================

header = """# coding=utf-8
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
        try:
            installed_version = pkg_resources.get_distribution(name).version
        except pkg_resources.DistributionNotFound:
            installed_version = "not-found"
        if installed_version != req_version:
            LOG.warning(
                f"EvaDB uses {name} {req_version}. The installed version is"
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

    # Do not add a header here
    # Releaser assumes the lines in the file to be related to version
    if file_path.endswith("version.py"):
        return

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
            #LOG.info("Formatting File : " + file_path)
            # ISORT
            isort_command = f"{ISORT_BINARY} --profile  black  {file_path}"
            os.system(isort_command)

            # AUTOPEP
            black_command = f"{BLACK_BINARY} -q {file_path}"
            os.system(black_command)

            # AUTOFLAKE
            autoflake_command = f"{FLAKE_BINARY} --config='{FLAKE8_CONFIG}' {file_path}"
            ret_val = os.system(autoflake_command)
            if ret_val:
                sys.exit(1)

            # PYLINT
            pylint_command = f"{PYLINT_BINARY} --spelling-private-dict-file {ignored_words_file} --rcfile={PYLINTRC}  {file_path}"
            #LOG.warning(pylint_command)
            #ret_val = os.system(pylint_command)
            #if ret_val:
            #    sys.exit(1)

            # CHECK FOR INVALID WORDS (like print)
            with open(file_path, 'r') as file:
                for line_num, line in enumerate(file, start=1):
                    if file_path not in IGNORE_PRINT_FILES and ' print(' in line:
                        LOG.warning(f"print() found in {file_path}, line {line_num}: {line.strip()}")
                        sys.exit(1)                        

    # END WITH

    fd.close()

# END FORMAT__FILE(FILE_NAME)

# check the notebooks
def check_notebook_format(notebook_file):
    # print(notebook_file)
    notebook_file_name = os.path.basename(notebook_file)

    # Ignore this notebook
    if notebook_file_name == "ignore_tag.ipynb":
        return True

    with open(notebook_file) as f:
        nb = nbformat.read(f, as_version=4)

    # Check that the notebook contains at least one cell
    if not nb.cells:
        LOG.error(f"ERROR: Notebook {notebook_file} has no cells")
        sys.exit(1)

    # Check that all cells have a valid cell type (code, markdown, or raw)
    for cell in nb.cells:
        if cell.cell_type not in ['code', 'markdown', 'raw']:
            LOG.error(f"ERROR: Notebook {notebook_file} contains an invalid cell type: {cell.cell_type}")
            sys.exit(1)

    # Check that all code cells have a non-empty source code
    for cell in nb.cells:
        if cell.cell_type == 'code' and not cell.source.strip():
            LOG.error(f"ERROR: Notebook {notebook_file} contains an empty code cell")
            sys.exit(1)
    
    # Check for "print(response)"
    # too harsh replaxing it
    # for cell in nb.cells:
    #     if cell.cell_type == 'code' and 'print(response)' in cell.source:
    #         LOG.error(f"ERROR: Notebook {notebook_file} contains an a cell with this content: {cell.source}")
    #         sys.exit(1)

    # Check for "Colab link"
    contains_colab_link = False
    for cell in nb.cells:
        if cell.cell_type == 'markdown' and 'colab' in cell.source:
            # Check if colab link is correct
            # notebook_file_name must match colab link
            if notebook_file_name in cell.source:
                contains_colab_link = True
                break

    if contains_colab_link is False:
        LOG.error(f"ERROR: Notebook {notebook_file} does not contain correct Colab link -- update the link.")
        sys.exit(1)

    return True

    # SKIP SPELL CHECK BY DEFAULT DUE TO PACKAGE DEPENDENCY
    # Need to install enchant-2 and aspell packages
    # apt-get install enchant-2 aspell

    import enchant
    from enchant.checker import SpellChecker
    chkr = SpellChecker("en_US")

    # Check spelling
    for cell in nb.cells:
        if cell.cell_type == "code":
            continue  # Skip code cells
        chkr.set_text(cell.source)
        for err in chkr:
            if err.word not in ignored_words:
                LOG.warning(f"WARNING: Notebook {notebook_file} contains the misspelled word: {err.word}")


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

@background
def check_file(file):
    #print(file)
    valid = False
    # only format the default directories
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
    parser.add_argument("-k", "--spell-check", help="enable spelling check (off by default)")

    args = parser.parse_args()

    # SOME SANITY CHECKS
    if args.add_header and args.strip_header:
        LOG.error("adding & stripping headers cannot be done together")
        sys.exit("adding & stripping headers cannot be done together")

    if args.file_name and args.dir_name:
        LOG.error("file_name and dir_name cannot be specified together")
        sys.exit("file_name and dir_name cannot be specified together")

    # CHECK IF FORMATTERS ARE INSTALLED
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
            "git merge-base origin/staging HEAD", 
            shell=True, 
            universal_newlines=True
        ).rstrip()
        files = (
            subprocess.check_output(
                f"git diff --name-only --diff-filter=ACRM {MERGEBASE} -- '*.py'",
                shell=True,
                universal_newlines=True
            )
            .rstrip()
            .split("\n")
        )

        for file in files:
            check_file(file)

    # CHECK ALL THE NOTEBOOKS

    # Iterate over all files in the directory 
    # and check if they are Jupyter notebooks
    for file in os.listdir(EvaDB_NOTEBOOKS_DIR):
        if file.endswith(".ipynb"):
            notebook_file = os.path.join(EvaDB_NOTEBOOKS_DIR, file)
            check_notebook_format(notebook_file)

    # SKIP SPELLING TESTS OVER PYTHON FILES BY DEFAULT
    if args.spell_check:

        # GO OVER ALL DOCS
        # Install aspell
        # apt-get install aspell
        
        #LOG.info("ASPELL")
        for elem in Path(EvaDB_DOCS_DIR).rglob('*.*'):
            if elem.suffix == ".rst" or elem.suffix == ".yml":
                os.system(f"aspell --lang=en --personal='{ignored_words_file}' check {elem}")

        os.system(f"aspell --lang=en --personal='{ignored_words_file}' check 'README.md'")

        # CODESPELL
        #LOG.info("Codespell")
        subprocess.check_output("codespell 'evadb/*.py'", 
                shell=True, 
                universal_newlines=True)
        subprocess.check_output("codespell 'evadb/*/*.py'", 
                shell=True, 
                universal_newlines=True)
        subprocess.check_output("codespell 'docs/source/*/*.rst'", 
                shell=True, 
                universal_newlines=True)
        subprocess.check_output("codespell 'docs/source/*.rst'", 
                shell=True, 
                universal_newlines=True)
        subprocess.check_output("codespell '*.md'", 
                shell=True, 
                universal_newlines=True)
        subprocess.check_output("codespell 'evadb/*.md'", 
                shell=True, 
                universal_newlines=True)

        for elem in Path(EvaDB_SRC_DIR).rglob('*.*'):
            if elem.suffix == ".py":
                os.system(f"aspell --lang=en --personal='{ignored_words_file}' check {elem}")

        for elem in Path(EvaDB_TEST_DIR).rglob('*.*'):
            if elem.suffix == ".py":
                os.system(f"aspell --lang=en --personal='{ignored_words_file}' check {elem}")