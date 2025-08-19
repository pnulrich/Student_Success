"""
validation.py
=============

Utility functions for validating DataFrame structure and safely parsing
tuple-like values in the student success framework.

This module centralizes lightweight validation and parsing helpers that
support consistent data handling across the package. Core functions include:

- ``validate_columns``: Ensures that a DataFrame contains all required columns,
  raising a clear error if any are missing.
- ``safe_parse_tuple``: Robustly parses tuple- or list-like data from strings,
  lists, or tuples while removing or normalizing invalid entries (e.g., NaN,
  None, empty strings).

Notes
-----
- ``validate_columns`` is useful in preprocessing pipelines to guarantee that
  downstream analysis functions have the columns they expect.
- ``safe_parse_tuple`` is designed to handle mixed or messy inputs (e.g., CSV
  exports where tuple-like values are stored as strings). It preserves list
  structure and replaces invalid entries with ``None`` for positional
  consistency.
- These utilities are general-purpose and not tied to institution-specific
  mappings.

Examples
--------
>>> import pandas as pd
>>> from student_success.utils import validation

# Validate required columns
>>> df = pd.DataFrame({"student_ID": [1, 2], "major": ["BIO", "CSC"]})
>>> validation.validate_columns(df.columns, ["student_ID", "major"])
# No error raised

>>> validation.validate_columns(df.columns, ["student_ID", "missing_col"])
Traceback (most recent call last):
    ...
ValueError: The following required columns are missing from your dataframe: missing_col

# Parse tuple-like strings
>>> validation.safe_parse_tuple("(BIO, CSC, PSY)")
['BIO', 'CSC', 'PSY']

>>> validation.safe_parse_tuple([1, None, 'nan', 'A'])
[1, None, None, 'A']

TODO
----
- Expand ``safe_parse_tuple`` with optional type enforcement
  (e.g., force integer parsing).
- Consider extending ``validate_columns`` with warnings for unexpected extras.
"""


import ast
import pandas as pd


def validate_columns(df_columns, required_columns):
    """
    Validates that all required columns are present in a DataFrame.

    Parameters
    ----------
    df_columns : iterable
        A list-like object (e.g., df.columns) containing the column names from a DataFrame.
    required_columns : list of str
        A list of column names expected to be present in the DataFrame.

    Raises
    ------
    ValueError
        If any of the required columns are missing, a ValueError is raised listing them.
    """

    missing_columns = []
    for column in required_columns:
        if column not in df_columns:
            missing_columns.append(column)
    if len(missing_columns) > 0:
        raise ValueError(f"The following required columns are missing from your dataframe: {', '.join(missing_columns)}")


def safe_parse_tuple(val):
    """
    Robustly parses list/tuple-like values from strings or native sequences,
    preserving structure and replacing invalid entries (e.g., NaN, None) with None.

    Parameters:
        val (str | tuple | list): Input to parse.

    Returns:
        list: List of parsed values, preserving positional structure.
    """
    # Case 1: Already a tuple or list
    if isinstance(val, (list, tuple)):
        return [
            x if pd.notna(x) and str(x).strip().lower() not in {'', 'nan', 'none'}
            else None
            for x in val
        ]

    # Case 2: String input – try literal_eval first
    if isinstance(val, str):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, (list, tuple)):
                return [
                    x if pd.notna(x) and str(x).strip().lower() not in {'', 'nan', 'none'}
                    else None
                    for x in parsed
                ]
        except (ValueError, SyntaxError):
            # Fallback to manual split
            items = val.strip("() ").split(",")
            return [
                x.strip().strip("'\"") if x.strip().lower() not in {'', 'nan', 'none'} else None
                for x in items
            ]

    # Case 3: Fallback
    return []
