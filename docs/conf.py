# -*- coding: utf-8 -*-
import os
import sys
import shutil
import warnings
from datetime import date

sys.path.insert(0, os.path.abspath(".."))

# -- Global variables

# The full version, including alpha/beta/rc tags
VERSION_DICT = {}
with open("../evadb/version.py", "r") as version_file:
    exec(version_file.read(), VERSION_DICT)

# Set the latest version.
LATEST_VERSION = VERSION_DICT["VERSION"]

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    "sphinxemoji.sphinxemoji",
    "sphinx_external_toc",
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_click.ext",
    "sphinx-jsonschema",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
#    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx_thebe",
    "sphinxcontrib.autodoc_pydantic",
    "sphinxcontrib.redoc",
    "sphinxcontrib.youtube",
    "sphinx_inline_tabs",
    "sphinx.ext.intersphinx",
    "myst_nb",
    "versionwarning.extension",
    "IPython.sphinxext.ipython_console_highlighting",
]

suppress_warnings = ["etoc.toctree", "myst.header"]

source_suffix = [".ipynb", ".html", ".md", ".rst"]

autodoc_pydantic_model_show_json = False
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_config_members = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_members = False
autodoc_pydantic_model_undoc_members = False

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
]


# Thebe configuration for launching notebook cells within the docs.
thebe_config = {
    "selector": "div.highlight",
    "repository_url": "https://github.com/georgia-tech-db/eva",
    "repository_branch": "master",
}

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "EvaDB"
copyright = str(date.today().year) + ", EvaDB."
author = u"EvaDB Team"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md", "images/reference/README.md"]


# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = "lovelace"

# List of substitutions
rst_prolog = """
.. |rst| replace:: restructuredText
"""
# -- Options for not found extension ---------------------------------------

# Template used to render the 404.html generated by this extension.
notfound_template = "404.html"

# Prefix added to all the URLs generated in the 404 page.
notfound_urls_prefix = ""

# -- Options for HTML output ----------------------------------------------

# The theme to use for pages.
html_theme = "furo"

html_title = project + "\n" + LATEST_VERSION
html_static_path = ["_static"]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for the theme, see the
# documentation.
html_theme_options = {
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-background-secondary": "#fff",
        "color-sidebar-background-border": "none",
    },
    "dark_css_variables": {
        "color-background-secondary": "#000",
    },
    # Add important announcement here
    "announcement": "<div class='topnav'></div>",
}

external_toc_path = "_toc.yml"  # optional, default: _toc.yml
external_toc_exclude_missing = False  # optional, default: False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", (None, "python-inv.txt"))
}


# Adding custom css file
html_static_path = ["_static"]
html_css_files = [
                    "custom.css", 
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css"]

# Check link: https://stackoverflow.com/questions/14492743/have-sphinx-report-broken-links/14735060#14735060
nitpicky = True
# BUG: https://stackoverflow.com/questions/11417221/sphinx-autodoc-gives-warning-pyclass-reference-target-not-found-type-warning
nitpick_ignore_regex = [('py:class', r'.*')]

# -- Initialize Sphinx ----------------------------------------------
def setup(app):
    warnings.filterwarnings(
        action="ignore",
        category=UserWarning,
        message=r".*Container node skipped.*",
    )
    # Custom JS
    app.add_js_file("js/top-navigation.js", defer="defer")
