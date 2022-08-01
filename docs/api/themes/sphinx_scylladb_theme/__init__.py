from os import getenv, path

import sphinx_collapse
import sphinx_copybutton
import sphinx_substitution_extensions
from notfound import extension as not_found
from sphinx_tabs import tabs

from themes.sphinx_scylladb_theme._version import version
from themes.sphinx_scylladb_theme.extensions import (
    hero_box,
    multiversion,
    navigation,
    panel_box,
    topic_box,
)
from themes.sphinx_scylladb_theme.lexers import cql, ditaa


def compute_toc_tree(toctree, maxdepth, collapse):
    if toctree:
        toctree_html = toctree(
            collapse=collapse,
            titles_only=True,
            maxdepth=maxdepth,
            includehidden=True,
        )
    else:
        toctree_html = ""
    toctree_html = navigation.get_navigation_tree(toctree_html, collapse)
    return toctree_html


def compute_hide_toc(context):
    if "toc" not in context:
        return True

    return navigation.side_nav_has_one_item(context["toc"])


def update_context(app, pagename, templatename, context, doctree):
    file_meta = context.get("meta", None) or {}
    context["scylladb_theme_version"] = version
    context["navigation_tree"] = compute_toc_tree
    context["full_width"] = "full-width" in file_meta
    context["hide_toc"] = compute_hide_toc(context)
    context["hide_pre_content"] = "hide-pre-content" in file_meta
    context["hide_post_content"] = "hide-post-content" in file_meta
    context["hide_version_warning"] = "hide-version-warning" in file_meta
    context["hide_sidebar"] = "hide-sidebar" in file_meta
    context["hide_secondary_sidebar"] = "hide-secondary-sidebar" in file_meta
    context["landing"] = "landing" in file_meta

    if (
        hasattr(app.config, "smv_rename_latest_version")
        and app.config.smv_rename_latest_version
    ):
        context["rename_latest_version"] = app.config.smv_rename_latest_version


def override_smv_latest_version(config):
    default = "master"
    if hasattr(config, "smv_latest_version") and config.smv_latest_version:
        default = config.smv_latest_version
    config.smv_latest_version = getenv("LATEST_VERSION", default=default)
    return config.smv_latest_version


def override_rst_epilog(config):
    substitutions = """
.. role:: raw-html(raw)
   :format: html

.. |v| replace:: :raw-html:`<i class="inline-icon fa fa-check" aria-hidden="true"></i>`
.. |x| replace:: :raw-html:`<i class="inline-icon fa fa-times" aria-hidden="true"></i>`
"""

    epilog = config.rst_epilog or ""
    config.rst_epilog = substitutions + epilog
    return config.rst_epilog


def update_config(app, config):
    override_smv_latest_version(config)
    override_rst_epilog(config)
    config.sphinx_tabs_disable_css_loading = True


def setup(app):
    """Setup theme"""
    app.add_html_theme("sphinx_scylladb_theme", path.abspath(path.dirname(__file__)))
    app.connect("html-page-context", update_context)
    app.connect("config-inited", update_config)

    """Setup lexers"""
    app.add_lexer("cql", cql.CQLLexer)
    app.add_lexer("ditaa", ditaa.DitaaLexer)

    """Setup thid-party extensions"""
    not_found.setup(app)
    sphinx_collapse.setup(app)
    sphinx_copybutton.setup(app)
    sphinx_substitution_extensions.setup(app)
    tabs.setup(app)

    """Setup custom extensions"""
    hero_box.setup(app)
    multiversion.setup(app)
    panel_box.setup(app)
    topic_box.setup(app)

    return {"version": version, "parallel_read_safe": True}
