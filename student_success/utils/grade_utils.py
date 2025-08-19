"""
grade_utils.py

Utilities for cleaning, simplifying, converting, and filtering course grades
in the student_success package.

This module provides functions that:
- Clean raw letter grades by removing institutional suffixes (repeat, renewal, etc.).
- Simplify detailed letter grades into A/B/C/D/F/W categories.
- Convert letter/symbolic grades to numeric GPA values using institutional rules.
- Normalize numeric grades to a 4.00 scale for cross‑institution comparisons.
- Filter DataFrames to include only valid grade categories.

Institutional Customization
---------------------------
Local grading conventions vary. Before use, confirm that your mappings in
`constants.py` reflect institutional policy.

- Letter→GPA mapping:
  `LETTER_GRADE_GPA_MAP` drives `num_grade_institutional()`. Update it if your
  institution uses different GPA points (e.g., no 4.33 for A+).
- Simplification rules:
  `GRADE_SIMPLIFICATION_MAP` is the baseline for `letter_grade_simplify()`.
  The `c_minus_flag` parameter controls whether "C-" counts as passing ("C")
  or non‑passing ("D").
- Special symbols:
  Expand `LETTER_GRADE_GPA_MAP` if you have additional codes (e.g., local
  withdrawal variants, audit types, in‑progress indicators).

Pitfalls
--------
- Suffixes and prefixes:
  Grades may include flags or leading dashes (e.g., "-W", "B^R", "C*", "A%").
  Use `strip_grade_suffixes()` (called internally where needed) before analysis.
- Category semantics:
  `num_grade_institutional()` returns:
    - GPA values for standard letters (e.g., 4.33 for A+, 2.00 for C),
    - `-1` for withdrawals (W, WF, PW),
    - `-2` for non‑graded/administrative statuses (e.g., WM, IP, I, AU),
    - `-3` for pass/fail categories (S/U).
  Downstream code should treat these negatives as flags, not numeric grades.
- Ordering:
  If you need both simplified letters and numeric conversions, run
  `letter_grade_simplify()` first, then apply filtering (`filter_valid_letter_grades()`),
  and only then convert to numeric/normalized values as needed.

Contents
--------
- strip_grade_suffixes(grade)
  Remove institutional suffixes/prefixes from a single grade string
  (e.g., "^R", "%", "@", "#", "*", leading "-").
- num_grade_institutional(grade)
  Convert a letter/symbolic grade to a numeric value using
  `LETTER_GRADE_GPA_MAP` (returns GPA or negative flags as noted above).
- num_grade_normalized(num_grade, institutional_max)
  Normalize a numeric grade to a 4.00 scale; returns -1 for invalid inputs.
- letter_grade_simplify(dataframe, c_minus_flag=True)
  Create `course_grade_letter_simp` from `course_grade_letter` by mapping to
  A/B/C/D/F/W (optionally treat "C-" as "D" when `c_minus_flag=True`).
- letter_grade_clean(dataframe)
  Clean `course_grade_letter` in a DataFrame by removing suffixes/prefixes; returns a copy.
- filter_valid_letter_grades(df, grade_col='course_grade_letter_simp',
  valid_grades=['A','B','C','D','F','W'])
  Return a filtered copy of `df` keeping only rows where `grade_col` is in `valid_grades`.

Notes
-----
- Depends on `LETTER_GRADE_GPA_MAP` and `GRADE_SIMPLIFICATION_MAP` from
  `student_success.utils.constants`.
- `letter_grade_simplify()` internally calls `strip_grade_suffixes()`; you don’t
  need to call `letter_grade_clean()` beforehand unless you want the cleaned
  values persisted to `course_grade_letter`.
"""


import pandas as pd
import re
from student_success.utils.constants import LETTER_GRADE_GPA_MAP, GRADE_SIMPLIFICATION_MAP


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

    if grade is None or pd.isna(grade):
        return grade

    grade_str = str(grade).strip().lstrip('-')  # remove leading dash from things like '-W'

    # Strip suffix characters and substrings: %, @, *, ^R, #, etc.
    return re.sub(r'\^R|[%#@*~]', '', grade_str)


def num_grade_institutional(grade):
    """
    Convert a letter or symbolic grade into its numeric equivalent using institutional GPA rules.

    Parameters
    ----------
    grade : str or float
        The course grade to be evaluated. May include suffixes (e.g., '%', '*', '^R'),
        be missing (None/NaN), or be a special symbolic code (e.g., "WM", "S").

    Returns
    -------
    float
        The corresponding numeric value:
        - GPA values (e.g., 4.33 for A+, 2.0 for C)
        - -1 for withdrawals (e.g., W, WF, PW)
        - -2 for incomplete, in-progress, audit, military withdrawal, or unrecognized grades
        - -3 for pass/fail grades (S/U)

    Notes
    -----
    - Removes suffixes and flags using `strip_grade_suffixes()` before processing.
    - Returns -2 for unrecognized or null grades.
    - GPA equivalents are defined in `LETTER_GRADE_GPA_MAP` (see `constants.py`).
    - Users can modify or extend this mapping in `constants.py` to fit institutional policy.

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
    fallback = -2  # Default for null, in-progress, audit, or unknown grades

    if pd.isnull(grade) or str(grade).lower() == 'nan':
        return fallback

    grade = strip_grade_suffixes(str(grade).strip().lstrip('-'))
    return LETTER_GRADE_GPA_MAP.get(grade, fallback)


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
        or num_grade > institutional_max
    ):
        return grade_normalized

    grade_normalized = 4 * num_grade / institutional_max  # This normalizes to a 4.00
    return grade_normalized


def letter_grade_simplify(dataframe, c_minus_flag=True):
    """
    Simplify detailed letter grades into broader categories: A, B, C, D, F, or W.

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
        Copy with 'course_grade_letter_simp' containing simplified values.

    Notes
    -----
    - Uses `strip_grade_suffixes()` to clean notations like C* or WF@.
    - Normalizes to uppercase after cleaning.
    - Treats known withdrawal and failure codes consistently.
    - Mapping is sourced from `GRADE_SIMPLIFICATION_MAP` in constants.py.
    - You may expand the map to reflect institutional or departmental policy.
    - Unmapped cleaned grades (e.g., 'IP', 'GH') are preserved as-is.
    """
    grade_map = GRADE_SIMPLIFICATION_MAP.copy()
    if c_minus_flag:
        grade_map["C-"] = "D"

    def simplify(grade):
        if pd.isnull(grade):
            return grade
        cleaned = strip_grade_suffixes(str(grade)).strip().upper()
        return grade_map.get(cleaned, cleaned)

    df_copy = dataframe.copy()
    df_copy['course_grade_letter_simp'] = df_copy['course_grade_letter'].apply(simplify)

    return df_copy


def letter_grade_clean(dataframe):
    """
    Clean raw letter grades by removing suffixes and leading dashes while preserving original grade distinctions.
    This is a thin wrapper function that could be replaced in code by df['course_grade_letter'] = df['course_grade_letter'].apply(strip_grade_suffixes)

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


def filter_valid_letter_grades(df: pd.DataFrame, grade_col: str = 'course_grade_letter_simp', valid_grades: tuple = ('A', 'B', 'C', 'D', 'F', 'W')) -> pd.DataFrame:
    """
    Filter rows to only include valid course grades.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing course attempts.
    grade_col : str, optional
        Name of the column with letter grades. Default is 'course_grade_letter_simp'.
    valid_grades : list of acceptable letter grade values

    Returns
    -------
    pd.DataFrame
        A filtered copy of the DataFrame, including only rows where `grade_col` is in `valid_grades`.
    """
    return df[df[grade_col].isin(valid_grades)].copy()
