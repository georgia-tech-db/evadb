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
import asyncio
from pprint import pprint
import git
import datetime
import pytz
import pkg_resources

background_loop = asyncio.new_event_loop()


def background(f):
    def wrapped(*args, **kwargs):
        return background_loop.run_in_executor(None, f, *args, **kwargs)

    return wrapped


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


def run_command(command_str: str):
    output = subprocess.check_output(
        command_str, shell=True, universal_newlines=True
    ).rstrip()

    pprint(output)
    return output


def get_changelog(LAST_RELEASE_COMMIT):
    unix_timestamp = int(run_command(f"git show -s --format=%ct {LAST_RELEASE_COMMIT}"))
    PREV_RELEASE_DATE = datetime.datetime.utcfromtimestamp(unix_timestamp).replace(
        tzinfo=pytz.UTC
    )

    # GO TO ROOT DIR
    os.chdir(EVA_DIR)

    # PULL CHANGES
    run_command("git pull origin master")

    # GET GIT HISTORY
    # Create the repository, raises an error if it isn't one.
    repo = git.Repo(".git")

    regexp = re.compile(r"\#[0-9]*")

    # Iterate through every commit for the given branch in the repository
    for commit in repo.iter_commits("master"):
        if commit.authored_datetime < PREV_RELEASE_DATE:
            break

        output = regexp.search(commit.message)

        if "[BUMP]" in commit.message:
            continue

        if output is None:
            continue

        else:
            pr_number = output.group(0)
            key_message = commit.message.split("\n")[0]
            key_message = key_message.split("(")[0]
            pr_number = pr_number.split("#")[1]
            print("* PR #" + str(pr_number) + ": " + key_message)


def read_file(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    import io

    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def release_version(NEXT_RELEASE):
    version_path = os.path.join(os.path.join(EVA_DIR, "eva"), "version.py")
    with open(version_path, "r") as version_file:
        output = version_file.read()
        output = output.replace("+dev", "")

    with open(version_path, "w") as version_file:
        version_file.write(output)

    run_command("git checkout -b release-" + NEXT_RELEASE)
    run_command("git add . -u")
    run_command("git commit -m '[RELEASE]: " + NEXT_RELEASE + "'")
    run_command("git push --set-upstream origin release-" + NEXT_RELEASE)


# ==============================================
# Main Function
# ==============================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Release eva")

    parser.add_argument(
        "-c",
        "--get-changelog",
        help="Retrieve the changelog by utilizing the last release commit provided. eg, 48ccb80237a456dd37834a7cba0b6fb4d2a8a7d8",
    )

    parser.add_argument(
        "-r",
        "--release-version",
        help="Publish a new version of EVA using the provided tag. eg, v0.2.0",
    )

    args = parser.parse_args()

    if args.get_changelog:
        get_changelog(args.get_changelog)

    if args.release_version:
        release_version(args.release_version)
