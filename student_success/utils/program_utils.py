import pandas as pd
import numpy as np
from student_success.utils.constants import MAJOR_ABBREV_TO_LABEL, MAJOR_TO_DISCIPLINE_DICT


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
    Full names are determined by the `MAJOR_ABBREV_LABEL` dictionary.
    This dictionary can be modified to reflect your institution's specific majors.
    """

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    return MAJOR_ABBREV_TO_LABEL.get(major, 'Other')
