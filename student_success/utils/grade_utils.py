import pandas as pd
import re

def strip_grade_suffixes(grade):
    """
    Remove common suffixes from grade strings that indicate special academic status.

    Parameters
    ----------
    grade : str or any
        The raw grade input. May be a string with suffixes (e.g., 'B^R', 'C*', 'A%') or a non-string (e.g., None, NaN).

    Returns
    -------
    str
        The cleaned grade string with suffixes removed. If input is None, returns None.

    Notes
    -----
    This function removes:
    - Repeat indicators (e.g., "^R")
    - Transfer/dishonesty/renewal flags ("% @ # *")
    """

    if grade is None:
        return grade

    grade_str = str(grade)

    # Strip suffix characters and substrings: %, @, *, ^R, #, etc.
    return re.sub(r'\^R|[%#@*]', '', grade_str)

def num_grade_institutional(grade):
    """
    Convert a letter or symbolic grade into its numeric equivalent using institutional GPA rules.

    Parameters
    ----------
    grade : str or float
        The course grade to be evaluated. May include suffixes, be missing (None/NaN), or be a special code (e.g., "WM", "S").

    Returns
    -------
    float
        The corresponding numeric value:
        - GPA values (e.g., 4.33 for A+, 2.0 for C)
        - -1 for withdrawals or unrecognized grades
        - -2 for incomplete/in-progress/military withdrawal/special codes
        - -3 for pass/fail grades

    Notes
    -----
    - Removes grade suffixes via `strip_grade_suffixes()` before processing.
    - "WM" = Military withdrawal (–2)
    - "W", "WF", etc. = Withdrawal (–1)
    - "S", "U" = Pass/Fail (–3)
    - "IP", "GP", "GH", "I" = Incomplete/in-progress (–2)
    - "V" or "N" =  audits and continuing education (-2)
    - Null values and unrecognized grades default to –1

    Examples
    --------
    >>> num_grade_institutional("A+")
    4.33
    >>> num_grade_institutional("C*")
    2.0
    >>> num_grade_institutional("W")
    -1
    >>> num_grade_institutional("WM")
    -2
    >>> num_grade_institutional("S")
    -3
    """

    # by default, unknown or missing situations will be coded as -1
    simp = -1

    if pd.isnull(grade):
        return simp

    if str(grade).lower() == 'nan':
        return -2

    grade = str(grade) # safely handle non-string situations

    # Manage situations where the transfer indicator (%), academic renewal indicator (#), dishonesty indicator (@), repeat to replace indicator (^R) and asterisk (*)are present
    grade = strip_grade_suffixes(grade)

    # Code all types of withdrawals as -1 except military withdrawals
    if grade == 'WM':
        return -2
    if 'W' in grade:
        return simp
    # code audits and continuing ed as a miscellaneous category (-2)
    if 'V' in grade or 'N' in grade:
        return -2
    # code pass/fail course grades as -3
    if 'S' in grade or 'U' in grade:
        return -3

    # IP = in progress
    # GP = grade pending
    # GH (unclear what this grade means) = ?
    # I = incomplete
    # nan = ?
    grade_map = {
        "A+": 4.33, "A": 4, "A-": 3.67,
        "B+": 3.33, "B": 3, "B-": 2.67,
        "C+": 2.33, "C": 2, "C-": 1.67,
        "D": 1, "F": 0,
        "IP": -2, "GP": -2, "GH": -2,
        "I": -2
    }

    return grade_map.get(grade, simp)


def num_grade_normalized(num_grade, institutional_max):
    """
    Normalize a numeric grade to a 4.00 scale for cross-institutional comparisons.

    Parameters
    ----------
    num_grade : int or float
        The student's numeric grade (e.g., 85 or 3.5).
    institutional_max : int or float
        The maximum possible grade at the institution (e.g., 100 or 4.33).

    Returns
    -------
    float
        A normalized grade on a 4.00 scale.
        Returns -1 if either input is invalid or normalization cannot be performed.

    Notes
    -----
    - If `num_grade` or `institutional_max` is missing, negative, or not a number, returns -1.
    - Grades above the maximum are also invalid and return -1.

    Examples
    --------
    >>> num_grade_normalized(85, 100)
    3.4
    >>> num_grade_normalized(4.33, 4.33)
    4.0
    >>> num_grade_normalized(None, 4.0)
    -1
    """

    grade_normalized = -1  # default to a -1 numeric grade

    # If num_grade or institutional_max is invalid, return -1 flag
    if (
        num_grade is None
        or num_grade == -1
        or not isinstance(num_grade, (int, float))
        or institutional_max == -1
        or not isinstance(institutional_max, (int, float))
    ):
        return grade_normalized
    elif institutional_max == -1 or not isinstance(institutional_max, (int, float)) or num_grade > institutional_max:
        return grade_normalized

    grade_normalized = 4 * num_grade / institutional_max  # This normalizes to a 4.00
    return grade_normalized

def letter_grade_simplify(dataframe, c_minus_flag = True):
    """
    Simplify letter grades into general categories, optionally treating 'C-' as non-passing.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        A DataFrame with a 'course_grade_letter' column to simplify.
    c_minus_flag : bool, optional
        If True (default), treat 'C-' as equivalent to 'D' (non-passing).
        If False, treat 'C-' as equivalent to 'C' (passing).

    Returns
    -------
    pandas.DataFrame
        A copy of the DataFrame with a new column 'course_grade_letter_simp' containing simplified grades.

    Notes
    -----
    - Removes suffixes before simplification (via `strip_grade_suffixes()`).
    - Merges A+, A, and A- into A, and similarly for other grades.
    - Converts withdrawal codes and failure codes to 'W' or 'F'.

    Examples
    --------
    'B-' → 'B'
    'C*' → 'C'
    'C-' → 'D' (if `c_minus_flag=True`)
    'WM' → 'W'
    """

    grade_mapping = {
        "A+": "A",
        "A": "A",
        "A-": "A",
        "B+": "B",
        "B": "B",
        "B-": "B",
        "C+": "C",
        "C": "C",
        "C-": "C" if not c_minus_flag else "D", # handles situations where C- are considered non-passing
        "D+": "D",
        "D": "D",
        "D-": "D",
        "FSA": "F",
        "F": "F",
        "WF": "F",
        "IF": "F",
        "UF": "F",
        "W": "W",
        "-W": "W",
        "WM": "W",
        "PW": "W"
        #GP = grade pending (typically during dishonesty charge process)
        #WM = military withdrawal
        #V = audit
        #N = continuing education grade (Perimeter College, legacy grade?)
        #@ suffix = dishonesty
        #% suffix = [don't know]
        ## suffix = [don't know]
    }

    df_copy = dataframe.copy()
    df_copy['course_grade_letter_simp'] = (
        df_copy['course_grade_letter']
        .apply(strip_grade_suffixes)
        .map(grade_mapping)
        .fillna(df_copy['course_grade_letter'])
    )
    return df_copy


def letter_grade_clean(dataframe):
    """
    Clean raw letter grades by removing suffixes while preserving original grade distinctions. This is a thin wrapper function that could be repalced in code by df['course_grade_letter'] = df['course_grade_letter'].apply(strip_grade_suffixes)

    Parameters
    ----------
    dataframe : pandas.DataFrame
        A DataFrame with a 'course_grade_letter' column to clean.

    Returns
    -------
    pandas.DataFrame
        A copy of the DataFrame with the 'course_grade_letter' column cleaned.

    Notes
    -----
    - Does not collapse grades (e.g., A- stays A-).
    - Removes suffixes like '*', '%', '@', '#', '^R'.
    - Intended for use before applying ordered grade logic (e.g., sorting or plotting).
    - Developed 2024-12-06 by Paul Ulrich because grades were being missed in calculus analyses if a student did repeat to replace or had some other not grade distinction
    listed. This was creating problems with ordered categories.

    Examples
    --------
    'B*' → 'B'
    'C#' → 'C'
    'A^R' → 'A'
    """

    df_copy = dataframe.copy()
    df_copy['course_grade_letter'] = df_copy['course_grade_letter'].apply(strip_grade_suffixes)
    return df_copy


def filter_valid_letter_grades(df: pd.DataFrame, grade_col: str = 'course_grade_letter_simp', valid_grades: list = ['A', 'B', 'C', 'D', 'F', 'W'] ) -> pd.DataFrame:
    """
    Filter rows to only include valid course grades.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing course attempts.
    grade_col : str, optional
        Name of the column with letter grades. Default is 'course_grade_letter_simp'.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame including only rows with valid grades.
    """
    return df[df[grade_col].isin(valid_grades)].copy()