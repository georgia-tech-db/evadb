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
from pprint import pprint
import git
import datetime
from datetime import date
import pytz
import pkg_resources
from datetime import datetime
import linecache
from semantic_version import Version
from typing import Dict
from github import Github

background_loop = asyncio.new_event_loop()


class SemanticVersionTypeEnum:
    PRERELEASE = "prerelease"  # 0.2.4+dev -> 0.2.4.alpha.1
    PATCH = "patch"  # 0.2.4+dev -> 0.2.5
    MINOR = "minor"  # 0.2.4+dev -> 0.3.0
    MAJOR = "major"  # 0.2.4+dev -> 1.0.0


def background(f):
    def wrapped(*args, **kwargs):
        return background_loop.run_in_executor(None, f, *args, **kwargs)

    return wrapped


def get_string_in_line(file_path, line_number):
    line = linecache.getline(file_path, line_number)
    return line.strip()


# ==============================================
# CONFIGURATION
# ==============================================

# NOTE: absolute path to evadb directory is calculated from current directory
# directory structure: evadb/scripts/formatting/<this_file>
# EvaDB_DIR needs to be redefined if the directory structure is changed
CODE_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
EvaDB_DIR = functools.reduce(
    os.path.join, [CODE_SOURCE_DIR, os.path.pardir, os.path.pardir]
)

# other directory paths used are relative to peloton_dir
EvaDB_SRC_DIR = os.path.join(EvaDB_DIR, "evadb")
EvaDB_CHANGELOG_PATH = os.path.join(EvaDB_DIR, "CHANGELOG.md")

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

    pprint(command_str)

    if "version" in command_str:
        pprint(output)
    return output


def get_changelog(github_timestamp):
    release_date = datetime.fromisoformat(github_timestamp[:-1])
    utc_timezone = pytz.timezone("UTC")
    release_date = utc_timezone.localize(release_date)

    # GO TO ROOT DIR
    os.chdir(EvaDB_DIR)

    # PULL CHANGES
    run_command("git pull origin master")

    # GET GIT HISTORY
    # Create the repository, raises an error if it isn't one.
    repo = git.Repo(".git")

    regexp = re.compile(r"\#[0-9]*")
    changelog = ""

    # Iterate through every commit for the given branch in the repository
    for commit in repo.iter_commits("master"):
        if commit.authored_datetime < release_date:
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

            if "[RELEASE]" in key_message:
                continue

            changelog += f"* PR #{pr_number}: {key_message}\n"

    return changelog


def read_file(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    import io

    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def release_version(current_version):
    version_path = os.path.join(os.path.join(EvaDB_DIR, "evadb"), "version.py")
    with open(version_path, "r") as version_file:
        output = version_file.read()
        output = output.replace("+dev", "")

    with open(version_path, "w") as version_file:
        version_file.write(output)

    NEXT_RELEASE = current_version  # without dev part

    run_command("git checkout -b release-" + NEXT_RELEASE)
    run_command("git add . -u")
    run_command("git commit -m '[RELEASE]: " + NEXT_RELEASE + "'")
    run_command("git push --set-upstream origin release-" + NEXT_RELEASE)

    # run_command(f"git tag -a {NEXT_RELEASE} -m '{NEXT_RELEASE} release'")
    run_command(f"git push origin release-{NEXT_RELEASE}")


def get_commit_id_of_latest_release(release_index=0):
    # Default to the latest release.
    import requests

    repo = "georgia-tech-db/evadb"
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url)
    data = response.json()

    latest_release = data[release_index]
    release_date = latest_release["created_at"]

    return release_date


def append_changelog(insert_changelog: str, version: str):
    with open(EvaDB_CHANGELOG_PATH, "r") as file:
        file_contents = file.read()

    # Location after ### [Removed] in file
    position = 327

    # Get rid of dev
    version = version.split("+")[0]

    today_date = date.today()
    header = f"##  [{version}] - {today_date}\n\n"

    modified_content = (
        file_contents[:position]
        + header
        + insert_changelog
        + "\n"
        + file_contents[position:]
    )

    with open(EvaDB_CHANGELOG_PATH, "w") as file:
        file.write(modified_content)


def publish_wheels(tag):
    run_command("rm -rf dist build")
    run_command("python3 setup.py sdist")
    run_command("python3 setup.py bdist_wheel")

    run_command(f"python3 -m pip install dist/evadb-{tag}-py3-none-any.whl")
    run_command("""python3 -c "import evadb; print(evadb.__version__)" """)

    print("Running twine to upload wheels")
    print("Ensure that you have .pypirc file in your $HOME folder")
    run_command("twine upload dist/* -r pypi")


def upload_assets(changelog, tag):
    # Authentication token
    access_token = os.environ["GITHUB_KEY"]
    # Repository information
    repo_owner = "georgia-tech-db"
    repo_name = "evadb"

    # Release information
    tag_name = "v" + tag
    assert "vv" not in tag
    asset_filepaths = [f"dist/evadb-{tag}-py3-none-any.whl", f"dist/evadb-{tag}.tar.gz"]

    # Create a PyGithub instance
    g = Github(access_token)

    # Get the repository
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    # Create the release
    release_name = tag_name
    release_message = f"{tag_name}\n\n {changelog}"

    # Publish the release
    release = repo.create_git_release(
        tag=tag_name,
        name=release_name,
        message=release_message,
        draft=False,
        prerelease=False,
    )

    # Retrieve the release by tag name
    release = repo.get_release(tag_name)

    # Upload assets to the release
    for filepath in asset_filepaths:
        asset_name = filepath.split("/")[-1]
        asset_path = Path(f"{EvaDB_DIR}/{filepath}")
        print("path: " + str(asset_path))
        release.upload_asset(str(asset_path), asset_name)

    print("Release created and published successfully.")


def bump_up_version(next_version):
    version_path = os.path.join(os.path.join(EvaDB_DIR, "evadb"), "version.py")

    major_str = get_string_in_line(version_path, 1)
    minor_str = get_string_in_line(version_path, 2)
    patch_str = get_string_in_line(version_path, 3)

    assert "dev" not in patch_str

    major_str = f"""_MAJOR = "{str(next_version.major)}"\n"""
    minor_str = f"""_MINOR = "{str(next_version.minor)}"\n"""
    patch_str = f"""_REVISION = "{str(next_version.patch)}+dev"\n\n"""

    footer = """VERSION_SHORT = f\"{_MAJOR}.{_MINOR}\"\nVERSION = f\"{_MAJOR}.{_MINOR}.{_REVISION}\""""
    output = major_str + minor_str + patch_str + footer

    with open(version_path, "w") as version_file:
        version_file.write(output)

    NEXT_RELEASE = f"v{str(next_version)}+dev"

    run_command("git checkout -b bump-" + NEXT_RELEASE)
    run_command("git add . -u")
    run_command("git commit -m '[BUMP]: " + NEXT_RELEASE + "'")
    run_command("git push --set-upstream origin bump-" + NEXT_RELEASE)
    run_command(f"gh pr create -B staging -H bump-{NEXT_RELEASE} --title 'Bump Version to {NEXT_RELEASE}' --body 'Bump Version to {NEXT_RELEASE}'")


# ==============================================
# Main Function
# ==============================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Release EvaDB")

    # version.py defines the VERSION and VERSION_SHORT variables
    VERSION_DICT: Dict[str, str] = {}
    with open("evadb/version.py", "r") as version_file:
        exec(version_file.read(), VERSION_DICT)

    VERSION = VERSION_DICT["VERSION"]

    parser.add_argument(
        "-n",
        "--next-release-type",
        type=str,
        choices=[
            SemanticVersionTypeEnum.PRERELEASE,
            SemanticVersionTypeEnum.PATCH,
            SemanticVersionTypeEnum.MINOR,
            SemanticVersionTypeEnum.MAJOR,
        ],
        help="Next version type.",
        required=True,
    )

    parser.add_argument(
        "-c",
        "--get-changelog",
        action="store_true",
        help="Retrieve the changelog since last release",
    )

    parser.add_argument(
        "-u",
        "--update-changelog",
        action="store_true",
        help="Update changelog.",
    )

    parser.add_argument(
        "-r",
        "--release-version",
        action="store_true",
        help="Publish a new version of EvaDB.",
    )

    parser.add_argument(
        "-p",
        "--publish-to-pypi",
        action="store_true",
        help="Create wheels and upload to PyPI.",
    )

    parser.add_argument(
        "-a",
        "--upload-assets",
        action="store_true",
        help="Upload assets on Github.",
    )

    parser.add_argument(
        "-b",
        "--bump-up-version",
        action="store_true",
        help="Bump up version.",
    )

    args = parser.parse_args()

    # FIGURE OUT NEXT VERSION

    current_version = VERSION
    version = Version(current_version)
    print("CURRENT VERSION: " + current_version)
    current_version_str_without_dev = current_version
    if "dev" in current_version:
        current_version_str_without_dev = current_version.split("+")[0]
    print("CURRENT VERSION WITHOUT DEV: " + current_version_str_without_dev)

    selected_release_type = args.next_release_type

    # Get the string representation of the next version
    if selected_release_type == SemanticVersionTypeEnum.PRERELEASE:
        next_version = version.next_patch()
        next_version_str = "v" + str(next_version) + ".alpha"
    elif selected_release_type == SemanticVersionTypeEnum.PATCH:
        next_version = version.next_patch()
        next_version_str = "v" + str(next_version)
    elif selected_release_type == SemanticVersionTypeEnum.MINOR:
        next_version = version.next_minor()
        next_version_str = "v" + str(next_version)
    elif selected_release_type == SemanticVersionTypeEnum.MAJOR:
        next_version = version.next_major()
        next_version_str = "v" + str(next_version)

    print("NEXT    VERSION : " + next_version_str)

    if args.get_changelog:
        release_date = get_commit_id_of_latest_release()
        changelog = get_changelog(release_date)
        print(changelog)

    if args.update_changelog:
        release_date = get_commit_id_of_latest_release()
        changelog = get_changelog(release_date)
        append_changelog(changelog, current_version_str_without_dev)

    if args.release_version:
        release_version(current_version_str_without_dev)

    if args.publish_to_pypi:
        publish_wheels(current_version_str_without_dev)

    if args.upload_assets:
        # We assume that we run each command sequentially here. When a new release
        # is made, the change log needs to be based on the second latest release.
        release_date = get_commit_id_of_latest_release(release_index=1)
        changelog = get_changelog(release_date)
        upload_assets(changelog, current_version_str_without_dev)

    if args.bump_up_version:
        bump_up_version(next_version)

    ## DO EVERYTHING BY DEFAULT
    is_all = not (
        args.get_changelog
        | args.update_changelog
        | args.release_version
        | args.publish_to_pypi
        | args.upload_assets
        | args.bump_up_version
    )

    if is_all:
        # GET CHANGELOG
        release_date = get_commit_id_of_latest_release()
        changelog = get_changelog(release_date)
        print(changelog)

        # UPDATE CHANGELOG
        append_changelog(changelog, current_version_str_without_dev)

        # RELEASE VERSION
        release_version(current_version_str_without_dev)

        # PUBLISH WHEELS ON PYPI
        publish_wheels(current_version_str_without_dev)

        # UPLOAD ASSETS ON GITHUB
        upload_assets(changelog, current_version_str_without_dev)

        # BUMP UP VERSION
        bump_up_version(next_version)
