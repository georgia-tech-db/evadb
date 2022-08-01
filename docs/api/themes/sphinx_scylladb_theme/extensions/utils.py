import os
import shutil
from urllib.parse import urlparse


def generate_template(template, **vars):
    """
    Replaces variables inside a template.

    :param template: Text with variables between brackets {}.
    :type src: str
    """

    return template.format(**vars)


def copy(src, dest):
    """
    Copies a file or a folder from src to dest.

    :param src: The path of the file to copy.
    :type src: str

    :param dest: The destination path.
    :type dest: str
    """

    if os.path.isfile(dest) or os.path.islink(dest):
        os.remove(dest)
    elif os.path.isdir(dest):
        shutil.rmtree(dest)
    if os.path.exists(src):
        try:
            shutil.copytree(src, dest)
        except Exception:
            shutil.copy(src, dest)


def build_redirect_body(path):
    """
    Builds the contents of the redirection file.

    :param path: Path to redirect to.
    :type path: str

    :return: HTML body of the redirection.
    :rtype: str
    """
    html = generate_template(
        """
        <html>
        <head>
        <meta http-equiv="refresh" content="0; url={path}">
        </head>
        </html>
        """,
        path=path,
    )
    return html


def is_url(path):
    """
    Checks if a path is an external url or a relative path.

    :param path: Path to evaluate.
    :type path: str

    :return: True if path is an external url.
    :rtype: bool
    """
    return bool(urlparse(path).netloc)
