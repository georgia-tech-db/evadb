"""
Extends sphinx_multiversion:
- GH Pages support
- 404 pages support
- Redirect to latest version
"""
import os

from .utils import build_redirect_body, copy


def add_gh_pages_support(app, exception):
    """
    Copies CNAME and .nojekyll files in the root of the output directory.

    :param app: Sphinx Application
    :type app: sphinx.application.Sphinx

    :param exception: Sphinx Error
    :type exception: sphinx.error.SphinxError
    """

    out_dir = app.builder.outdir
    head, tail = os.path.split(out_dir)

    copy(out_dir + "/CNAME", head + "/CNAME")
    copy(out_dir + "/.nojekyll", head + "/.nojekyll")


def add_notfound_support(app, exception):
    """
    Creates a 404.html in the root of the output directory.

    :param app: Sphinx Application
    :type app: sphinx.application.Sphinx

    :param exception: Sphinx Error
    :type exception: sphinx.error.SphinxError
    """
    out_dir = app.builder.outdir
    head, tail = os.path.split(out_dir)

    copy(out_dir + "/404.html", head + "/404.html")
    copy(out_dir + "/_static", head + "/_static")


def add_notfound_support_dirhtml(app, exception):
    """
    Creates a 404.html in the root of the output directory.

    :param app: Sphinx Application
    :type app: sphinx.application.Sphinx

    :param exception: Sphinx Error
    :type exception: sphinx.error.SphinxError
    """
    out_dir = app.builder.outdir
    head, tail = os.path.split(out_dir)

    if app.builder.name == "dirhtml" and os.path.exists(out_dir + "/404"):
        copy(out_dir + "/404/index.html", out_dir + "/404.html")


def create_redirect_to_latest_version(app, exception):
    """
    When multiversion is enabled, creates a redirect to the ``smv_latest_version``
    defined in ``conf.py``.

    :param app: Sphinx Application
    :type app: sphinx.application.Sphinx

    :param exception: Sphinx Error
    :type exception: sphinx.error.SphinxError
    """

    latest_dir = app.config.smv_latest_version
    if (
        hasattr(app.config, "smv_rename_latest_version")
        and app.config.smv_rename_latest_version
    ):
        latest_dir = app.config.smv_rename_latest_version

    out_dir = app.builder.outdir
    head, tail = os.path.split(out_dir)

    with open(os.path.join(head + "/index.html"), "w+") as t_file:
        t_file.write(build_redirect_body(latest_dir))


def setup(app):
    is_multiversion = os.getenv("SPHINX_MULTIVERSION_NAME")
    if is_multiversion:
        app.connect("build-finished", add_gh_pages_support)
        app.connect("build-finished", add_notfound_support)
        app.connect("build-finished", create_redirect_to_latest_version)
    else:
        app.connect("build-finished", add_notfound_support_dirhtml)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
