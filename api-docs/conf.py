# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src/'))

import sphinx_rtd_theme

# -- Project information -----------------------------------------------------

project = 'EVA'
copyright = '2018-2020, Georgia Tech Database Group'
author = 'Georgia Tech Database Group'

# The full version, including alpha/beta/rc tags
release = '0.0.1'

master_doc = 'index'

html_theme = 'mps'
html_sidebars = {
    '**': ['localtoc.html', 'relations.html', 'links.html', 'contact.html'],
}

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx',
    'sphinx.ext.todo', 'sphinx.ext.mathjax', 'sphinx.ext.viewcode',
    'sphinx.ext.napoleon', 'sphinx.ext.graphviz', 'extensions.mps'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix of source filenames.
source_suffix = '.rst'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

highlight_language = 'python'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# MOCK_MODULES = ['numpy', 'sqlalchemy', 'petastorm', 'sqlalchemy.orm']
# for mod_name in MOCK_MODULES:
#     sys.modules[mod_name] = mock.Mock()

autodoc_mock_imports = ["numpy", "sqlalchemy", "sqlalchemy_utils",
                        "petastorm", "yaml", "pyspark"]
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'sphinx_rtd_theme'

# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_path = ['themes']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
