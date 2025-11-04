# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathlib, re

project = 'student_success'
copyright = '2025, Paul Ulrich'
author = 'Paul Ulrich'
author_handle = 'pnulrich'

version_file = pathlib.Path(__file__).parents[2] / "student_success" / "_version.py"
m = re.search(r'__version__\s*=\s*"([^"]+)"', version_file.read_text())
release = version = m.group(1) if m else "0.0.0"
html_baseurl = f'https://github.com/{author_handle}/{project}'

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

exclude_patterns = [
    "_build",
    '**/deprecated*',
    "Thumbs.db",
    ".DS_Store",
    "student_success.WVU*",
    "student_success.deprecated*",
    "student_success.entropy*",
    "student_success.demographics_grad_combine*",
]
add_module_names = False
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_show_sourcelink = False # suppresses the "View page source" link that occurs on every page when using the viewcode extension
html_css_files = ["css/custom.css"]  # custom style sheet to stretch content up to 1200 pixels wide