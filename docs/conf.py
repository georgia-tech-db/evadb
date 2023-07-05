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
    "sphinx.ext.autosectionlabel",
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
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

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
    "navigation_with_keys": True,
    # Add important announcement here
    # "announcement": "<em>Important</em> announcement!"
}

external_toc_path = "_toc.yml"  # optional, default: _toc.yml
external_toc_exclude_missing = False  # optional, default: False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", (None, "python-inv.txt"))
}


# Adding custom css file
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Adding the Tutorial notebooks to ./docs/source/tutorials/

for i in os.listdir("../tutorials"):
    if i.endswith(".ipynb"):
        shutil.copy(f"../tutorials/{i}", "./source/tutorials/")

jupyter_execute_notebooks = "off"


# -- Initialize Sphinx ----------------------------------------------
def setup(sphinx):
    warnings.filterwarnings(
        action="ignore",
        category=UserWarning,
        message=r".*Container node skipped.*",
    )
