# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'student_success'
copyright = '2025, Paul Ulrich'
author = 'Paul Ulrich'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',  # supports Google and numpy docstrings
    'sphinx.ext.viewcode',  # include links to source code
    'sphinx.ext.githubpages'
]

import os, sys
sys.path.insert(0, os.path.abspath('../..'))

templates_path = ['_templates']
exclude_patterns = ['**/deprecated*']

add_module_names = False
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']