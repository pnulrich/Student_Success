"""
The ``preprocess`` module provides standardized cleaning utilities for
course attempt data used in Markov diagram analysis. These functions
prepare student-level course sequences by constraining attempts and
removing redundant data, ensuring that downstream visualizations
reflect meaningful academic pathways.

Functions
---------
- limit_attempts :
    Restricts the number of course attempts per student to a specified
    maximum (default: two attempts).
- exclude_unnecessary_subsequent_attempts :
    Removes later attempts if a student successfully passed on the
    first attempt, preventing artificial inflation of repeat patterns.
- prepare_course_attempts :
    Applies the standard cleaning pipeline (limit attempts + drop
    unnecessary repeats) to produce a streamlined dataset ready for
    Markov diagram construction.

Notes
-----
- These preprocessing functions should be applied after filtering to
  valid letter grades via
  ``utils.grade_utils.filter_valid_letter_grades()``.
- Output is designed to integrate directly with the graph construction
  utilities in ``markov_diagrams.graph_builder``.
"""


def limit_attempts(df, max_attempts=2):
    """
    Limit each student's data to at most `max_attempts` rows.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing course attempt records with 'student_ID'.
    max_attempts : int, optional
        Maximum number of attempts to retain per student. Default is 2.

    Returns
    -------
    pd.DataFrame
        DataFrame where each student_ID has at most `max_attempts` attempts retained.
        The earliest attempts are kept based on sort order.
    """
    df = df.sort_values(by=['student_ID', 'course_term'])
    return df.groupby('student_ID').head(max_attempts).reset_index(drop=True)


def exclude_unnecessary_subsequent_attempts(df, grade_col='course_grade_letter_simp', passing_grades=('A', 'B', 'C')):
    """
    Drop all subsequent attempts for students who passed the course on their first attempt.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of course attempts, sorted by 'student_ID' and 'course_term'.
    grade_col : str, optional
        Column name containing the simplified letter grades. Default is 'course_grade_letter_simp'.
    passing_grades : tuple, optional
        tuple of grades considered passing. Default is ['A', 'B', 'C'].

    Returns
    -------
    pd.DataFrame
        DataFrame with downstream attempts removed if the first was a passing grade.
    """
    df = df.sort_values(by=['student_ID', 'course_term'])
    to_drop = []

    for student_id, group in df.groupby('student_ID'):
        if len(group) > 1:
            first_grade = group.iloc[0][grade_col]
            if first_grade in passing_grades:
                to_drop.extend(group.index[1:])  # drop all attempts after first

    return df.drop(index=to_drop)


def prepare_course_attempts(df):
    """
    Apply a standardized cleaning pipeline to prepare course attempt data.

    The pipeline includes:
    - Limiting students to a maximum of 2 attempts
    - Dropping second attempts if the first was a passing grade

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame containing course attempts.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for analysis or visualization.

    Notes
    -------
    Before running this, ensure that filtering to valid letter grades (utils.grade_utils.filter_valid_letter_grades())
    is applied as needed.
    """
    df = limit_attempts(df)
    df = exclude_unnecessary_subsequent_attempts(df)
    return df
