# coding=utf-8
# Copyright 2018-2022 EVA
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

# -- Path setup --------------------------------------------------------------

import os
import sys
import warnings
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from datetime import datetime

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('../'))


# Temp. workaround for
# https://github.com/agronholm/sphinx-autodoc-typehints/issues/133
warnings.filterwarnings(
    'ignore', message='sphinx.util.inspect.Signature\(\) is deprecated')


# -- Project information -----------------------------------------------------
project = "evadb"
author = "Georgia Tech Database Group"
copyright = str(datetime.now().year) + f', {author}'

# The full version, including alpha/beta/rc tags
from eva.version import __version__ as version

release =  version

master_doc = 'index'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_external_toc",
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    "myst_nb",
    "sphinx-jsonschema"
]

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

external_toc_exclude_missing = True
external_toc_path = "_toc.yml"

autosummary_generate = False  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries

# Remove 'view source code' from top of page (for html, not python)
html_show_sourcelink = False
# If no class summary, inherit base class summary
autodoc_inherit_docstrings = False
numpydoc_show_class_members = False


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# highlight_language = 'python'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

autodoc_mock_imports = ["numpy", "sqlalchemy", "sqlalchemy_utils",
                        "sqlalchemy.orm", "sqlalchemy.orm.exc",
                        "sqlalchemy.types",
                        "petastorm", "yaml", "pyspark", "torch",
                        "pandas", "cv2", "eva.catalog"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "repository_url": "https://github.com/georgia-tech-db/Eva",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "path_to_docs": "api-docs/",
    "home_page_in_toc": False
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

autodoc_default_flags = ['members', 'private-members', 'special-members',
                         # 'undoc-members',
                         'show-inheritance']


def autodoc_skip_member(app, what, name, obj, skip, options):
    # Ref: https://stackoverflow.com/a/21449475/
    exclusions = ('__weakref__',  # special-members
                  '__doc__', '__module__', '__dict__',  # undoc-members
                  )
    exclude = name in exclusions
    return True if exclude else None


def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)
    app.add_css_file('custom.css')
