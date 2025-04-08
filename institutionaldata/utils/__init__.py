"""
Utility functions for data wrangling and processing in institutionaldata.

Submodules included:
- io_utils: Tools for file I/O, including column renaming from codebooks.
- scrambler: Functions for anonymizing and restoring student IDs.
- grades, time_utils, matriculation, etc.: Additional support modules.
"""

from .io_utils import (
    load_grades,
    rename_columns_in_bulk,
    extract_column_mapping,
    flatten_column_mapping,
)

from .scrambler import (
    scramble_ID,
    unscramble_ID
)