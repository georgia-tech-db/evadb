import os
import urllib.request


def download_story():
    parsed_file_path, orig_file_path = "new_wp.txt", "wp.txt"
    if not os.path.exists(parsed_file_path):
        urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/2600/pg2600.txt", orig_file_path)

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
    whitelist = set("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    with open(path, "r") as f:
        for line in f.readlines():
            for i in range(0, len(line), num_token):
                cut_line = line[i : min(i + 1000, len(line))]
                cut_line = "".join(filter(whitelist.__contains__, cut_line))
                yield cut_line


def try_execute(conn, query):
    try:
        conn.query(query).execute()
    except Exception:
        pass