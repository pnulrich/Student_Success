# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'student_success'
copyright = '2025, Paul Ulrich'
author = 'Paul Ulrich'
release = '0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # supports Google and numpy docstrings
    'sphinx.ext.viewcode',  # include links to source code
    'sphinx.ext.githubpages'
]

import os, sys
sys.path.insert(0, os.path.abspath('../..'))

templates_path = ['_templates']
exclude_patterns = []

# not sure if the exclude_patterns is necessary
# exclude_patterns = ['venv', '.gitignore', 'Results', 'R Scripts', 'jupyter_notebooks', '.ipynb_checkpoints', 'main.py', 'make.bat', 'Makefile', 'ScratchBucket']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']