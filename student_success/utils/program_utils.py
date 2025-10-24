"""
Utility functions for handling major abbreviations, full names, and discipline
classifications.

This module centralizes common operations for translating and standardizing
academic program codes. Functions include:

- Mapping major abbreviations to broader discipline groups for analysis
  (e.g., Biology → bio_sci, CSC → eng_CS).
- Converting major abbreviations to full descriptive names using
  institution-specific mappings.
- Normalizing premajor abbreviations (e.g., PNUR → NUR) so that premajors
  and their mature equivalents are treated consistently.

The mappings used here are defined in ``student_success.utils.constants``:

- ``MAJOR_ABBREV_TO_LABEL`` provides human-readable names for major abbreviations.
- ``MAJOR_TO_DISCIPLINE_DICT`` maps abbreviations to discipline categories.
- ``PREMAJOR_TO_MAJOR_DICT`` defines how premajors are converted to their
  mature major equivalents.

Notes
-----
- These utilities assume input values are either major abbreviations (strings)
  or missing values (NaN).
- If an abbreviation is not found in the mapping dictionaries, default
  categories (e.g., "Other" or "non_STEM") are returned.
- For end users: ensure abbreviations and premajors are standardized using
  ``replace_premajor_abbreviations`` or by enabling the
  ``pre_major_conversion`` flag in ``lookup_major_name``.

Examples
--------
>>> classify_discipline('BIO')
'bio_sci'

>>> lookup_major_name('CSC')
'Computer Science'

>>> replace_premajor_abbreviations('PNUR')
'NUR'
"""


import pandas as pd
import numpy as np
from student_success.utils.constants import MAJOR_ABBREV_TO_LABEL, MAJOR_TO_DISCIPLINE_DICT, PREMAJOR_TO_MAJOR_DICT


def classify_discipline(major):
    """
    Map major abbreviations to discipline categories using MAJOR_TO_DISCIPLINE_DICT.

    Parameters
    ----------
    major : str or NaN
        Abbreviation of the major (e.g., 'BIO', 'CSC', etc.).

    Returns
    -------
    str or NaN
        Discipline group: 'bio_sci', 'phy_sci', 'eng_CS', 'other_STEM', 'undeclared', or 'non_STEM'.
    """
    if pd.isna(major):
        return np.nan
    return MAJOR_TO_DISCIPLINE_DICT.get(major, 'non_STEM')


def lookup_major_name(major, pre_major_conversion=False):
    """
    Returns the full name of a major given its abbreviation using a predefined mapping.

    This function takes a major abbreviation as input and returns the corresponding
    full name of the major using a predefined dictionary `majors_dict`. If the
    abbreviation is not found in the dictionary, the function returns 'Other'.
    If the input is missing (NaN), it returns NaN.

    Parameters:
    -----------
    major : str or NaN
        The abbreviation of the major (e.g., 'BIO', 'CSC', etc.).

    Returns:
    --------
    str or NaN
        The full name of the major corresponding to the abbreviation. Possible
        return values include the full names like 'Biology', 'Computer Science',
        'Psychology', 'Other', or NaN (for missing values).

    Notes:
    --------
    Full names are determined by the `MAJOR_ABBREV_LABEL` dictionary.
    This dictionary can be modified to reflect your institution's specific majors.
    Consider processing with replace_premajor_abbreviations beforehand or use
    pre_major_conversion = True.
    """

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    elif pre_major_conversion == False:
        return MAJOR_ABBREV_TO_LABEL.get(major, 'Other')
    else:
        raw_major = PREMAJOR_TO_MAJOR_DICT.get(major, major)
        return MAJOR_ABBREV_TO_LABEL.get(raw_major, 'Other')


def replace_premajor_abbreviations(major):
    """
    Returns abbreviation for the "mature" major given abbreviation for a premajor using a predefined mapping .

    This function takes a major abbreviation as input and returns the corresponding
    abbreviation of the "mature" major using a predefined dictionary `PREMAJOR_TO_MAJOR_DICT`. If the
    abbreviation is not found in the dictionary, the function returns major.
    If the input is missing (NaN), it returns NaN.

    Parameters:
    -----------
    major : str or NaN
        The abbreviation of the premajor or major (e.g., 'PNUR', 'BNUR', etc.).

    Returns:
    --------
    str or NaN
        The abbreviation of the "mature" major corresponding to a  premajor abbreviation.

    Notes:
    --------
    Abbreviations for the "mature" majors are determined by `PREMAJOR_TO_MAJOR_DICT`.
    This dictionary can be modified to reflect your institution's specific majors.
    """

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    return PREMAJOR_TO_MAJOR_DICT.get(major, major)
