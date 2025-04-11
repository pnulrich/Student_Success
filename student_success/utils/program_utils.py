import pandas as pd
import numpy as np
from student_success.utils.constants import MAJORS_DICT, DISCIPLINE_DICT


def classify_discipline(major):
    """
    Map major abbreviations to discipline categories.

    This function takes a major abbreviation as input and returns the corresponding
    discipline category. The function uses a dictionary `discipline_dict` to map
    certain major codes (e.g., 'BIO', 'BNUR') to their respective disciplines
    (e.g., 'Biology', 'STEM-Related', 'Other STEM'). If the major is not found in
    the dictionary, it categorizes the major as 'Non-STEM'. If the major is missing
    (NaN), it returns NaN.

    Parameters:
    -----------
    major : str or NaN
        The major abbreviation code to be categorized (e.g., 'BIO', 'CSC', etc.).

    Returns:
    --------
    str or NaN
          The discipline category based on the mapping. Possible return values include:
          'Biology', 'STEM-Related', 'Other STEM', 'Non-STEM', or NaN (for missing values).

      Notes
      -----
      The classification is determined by the `DISCIPLINE_DICT` dictionary.
      You may customize or expand this dictionary to reflect the categories used at your institution.
      """

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    return DISCIPLINE_DICT.get(major, 'Non-STEM')


def lookup_major_name(major):
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
    Full names are determined by the `MAJORS_DICT` dictionary.
    This dictionary can be modified to reflect your institution's specific majors.
    """

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    return MAJORS_DICT.get(major, 'Other')
