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
import os
import urllib.request


def download_story():
    parsed_file_path, orig_file_path = "new_wp.txt", "wp.txt"
    if not os.path.exists(parsed_file_path):
        urllib.request.urlretrieve(
            "https://www.gutenberg.org/cache/epub/2600/pg2600.txt", orig_file_path
        )

    # Process file each paragraph per line.
    new_f = open(parsed_file_path, "w")
    merge_line = ""
    with open(orig_file_path, "r") as f:
        for line in f.readlines():
            if line == "\n":
                new_f.write(f"{merge_line}\n")
                merge_line = ""
            else:
                merge_line += line.rstrip("\n") + " "

    return parsed_file_path


def read_text_line(path, num_token=1000):
    # For simplicity, we only keep letters.
    whitelist = set(".!?abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    with open(path, "r") as f:
        line_itr = 0
        for line in f.readlines():
            line_itr = line_itr + 1
            if line_itr % 10 == 0:
                print("line: " + str(line_itr))
            for i in range(0, len(line), num_token):
                cut_line = line[i : min(i + 1000, len(line))]
                cut_line = "".join(filter(whitelist.__contains__, cut_line))
                yield cut_line

            if line_itr == 1000:
                break


def try_execute(conn, query):
    try:
        conn.query(query).execute()
    except Exception:
        pass
