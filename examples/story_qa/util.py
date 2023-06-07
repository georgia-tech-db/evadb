import os
import urllib.request


def download_story():
    # Thanks to Project Gutenberg, we use Pride and Prejudice for our
    # demonstration purpose.
    if not os.path.exists("new_pp.txt"):
        urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/1342/pg1342.txt", "pp.txt")

    # Process file each paragraph per line.
    new_f = open("new_pp.txt", "w")
    merge_line = ""
    with open("pp.txt", "r") as f:
        for line in f.readlines():
            if line == "\n":
                new_f.write(f"{merge_line}\n")
                merge_line = ""
            else:
                merge_line += line.rstrip("\n") + " "

    return "new_pp.txt"


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