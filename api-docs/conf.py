# -*- coding: utf-8 -*-
import os
import sys
import warnings
from datetime import date

sys.path.insert(0, os.path.abspath(".."))

# -- Global variables

# The full version, including alpha/beta/rc tags
VERSION_DICT = {}
with open("../eva/version.py", "r") as version_file:
    exec(version_file.read(), VERSION_DICT)

# Set the latest version.
LATEST_VERSION = VERSION_DICT["VERSION"]

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx.ext.extlinks",
    "sphinx_sitemap",
    "recommonmark",  # optional
    "sphinx_external_toc",
    "sphinx_design",
]

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "EVA Video Database System"
copyright = str(date.today().year) + ", Georgia Tech Database Group."
author = u"Georgia Tech Database Group"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

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
#html_theme_path = ["themes"]


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for the theme, see the
# documentation.
html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}

external_toc_path = "_toc.yml"  # optional, default: _toc.yml
external_toc_exclude_missing = False  # optional, default: False

html_logo = "_static/mascots/Logo.png"

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

# Adding custom added css files
html_static_path = ['_static']
html_css_files = ['custom.css']

# -- Initialize Sphinx ----------------------------------------------
def setup(sphinx):
    warnings.filterwarnings(
        action="ignore",
        category=UserWarning,
        message=r".*Container node skipped.*",
    )

