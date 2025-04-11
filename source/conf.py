# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# to update the docs, run the following two commands:
# sphinx-apidoc -o source ../HHMI_Student_Success/student_success
# sphinx-build -E -b html source build

import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import student_success.successmetrics
import student_success.utilityfunctions


project = 'HHMI Student Success - Project B'
copyright = '2024, Paul Ulrich'
author = 'Paul Ulrich'
release = '0.1'

# List modules you want to mock (if any)
autodoc_mock_imports = ["pandas", "tkinter", "re"]

# Define the default flags for autodoc
autodoc_default_flags = [
    "members",
    "undoc-members",
    "show-inheritance"
]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
# Set the output directory for HTML builds
html_output_path = '_build/doc/'

exclude_patterns = ['venv', '.gitignore', 'Results', 'R Scripts', 'jupyter_notebooks', '.ipynb_checkpoints', 'main.py', 'make.bat', 'Makefile', 'ScratchBucket']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
