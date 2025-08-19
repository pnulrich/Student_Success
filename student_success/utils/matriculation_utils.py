import pandas as pd
import numpy as np
from student_success.utils.validation import validate_columns

"""
matriculation_utils.py

(DEPRECATED) Utilities for handling matriculation term fields in Banner
or similar student information systems.

These functions attempt to clean, adjust, and validate matriculation
term values, but institutional data often makes them unreliable.  
In particular, Banner may not report `matriculation_term` consistently
due to program-level timing differences, back-dated entries, or
misalignment with the first actual course term.  

**Recommendation:**  
Instead of relying on Banner’s `matriculation_term`, create a program-
specific `term_earliest` column using the earliest term a student
actually enrolled in courses. This avoids the pitfalls that motivated
these utilities to be retired.

Institutional Customization
---------------------------
If you do use these functions:
- Confirm that your SIS codes `matriculation_term` consistently with
  the program of interest.
- Use `demographics_term` or other enrollment-based fields as a
  fallback when no matching demographics exist for a student’s
  official matriculation term.

Pitfalls
--------
- Students may have multiple distinct `matriculation_term` values.
  Filtering logic must decide whether to exclude or include them.
- Demographic datasets covering a limited range may miss records for
  the true matriculation term, causing misalignment.
- Graduation-level parsing assumes consistent use of codes
  (e.g., `'B'` for bachelor’s).

Contents
--------
- extract_bachelors_graduation_date(df) :
  Add `graduation_date_bachelors` column, containing the earliest
  awarded bachelor’s graduation date per student.
- filter_by_valid_matriculation_term(df, student_id_col='student_ID',
  term_col='matriculation_term', demo_term_col='demographics_term') :
  Retain only students where `demographics_term` matches their minimum
  matriculation term.
- clean_and_adjust_matriculation(df, ..., include_multiple_matriculations=0,
  demographics_range_min=None) :
  Compute adjusted matriculation term (`matriculation_term_adjusted`) by
  aligning Banner values with the earliest available demographics term,
  optionally excluding students with multiple matriculation terms.

Notes
-----
- These functions are retained for legacy compatibility but are not
  recommended for new analyses.
- Prefer constructing a robust `term_earliest` column based on actual
  enrollment activity.
"""


def extract_bachelors_graduation_date(df):
    """
    This function accepts a dataframe with at least 'graduation_level', 'graduation_date', and 'graduation_status' columns.
    It returns the dataframe with a new column 'graduation_date_bachelors', which holds the earliest
    bachelor's graduation date ('B') for students with a corresponding 'Awarded' status.
    """

    def get_earliest_bachelors_date(levels, dates, statuses):
        # Ensure the tuples are iterable and contain non-null values
        if isinstance(levels, tuple) and 'B' in levels:
            try:
                # Get all indices of bachelor's level ('B')
                indices_of_b = [i for i, level in enumerate(levels) if level == 'B']
                # Check if any of the corresponding statuses are 'Awarded'
                awarded_indices = [i for i in indices_of_b if i < len(statuses) and statuses[i] == 'Awarded']

                if awarded_indices:
                    # Get the corresponding graduation dates for all 'Awarded' 'B' and return the earliest one
                    corresponding_dates = [dates[i] for i in awarded_indices if i < len(dates)]
                    # Convert dates to datetime to find the earliest one
                    corresponding_dates = pd.to_datetime(corresponding_dates, errors='coerce')
                    return corresponding_dates.min()  # Return the earliest date
            except Exception:
                return np.nan  # In case of any errors, return NaN
        return np.nan  # No 'B' found or invalid tuple

    # Apply the function to each row and create a new column 'graduation_date_bachelors'
    df['graduation_date_bachelors'] = df.apply(
        lambda row: get_earliest_bachelors_date(row['graduation_level'], row['graduation_date'],
                                                row['graduation_status']),
        axis=1
    )
    return df


def filter_by_valid_matriculation_term(demographics_df, student_id_col='student_ID', term_col='matriculation_term',
                                       demo_term_col='demographics_term'):
    """
    Cleans the DataFrame by identifying and keeping only rows for student_ID's that have a
    demographics term associated with the minimum matriculation term. This avoids issues
    that occur when a dataset for various years includes demographics but the dataset does not go
    back far enough in time to get demographics associated with their first term.

    Parameters:
    - demographics_df (pd.DataFrame): DataFrame containing course and student information.
    - student_id_col (str): Column name for student ID.
    - term_col (str): Column name for the term of matriculation.
    - demo_term_col (str): Column name for the demographics term.

    Returns:
    - pd.DataFrame: A cleaned DataFrame containing only the rows where the demographics term
      matches the minimum term of matriculation for each student and at least one valid match exists.
    """

    demographics_df = demographics_df.copy()
    validate_columns(demographics_df.columns, required_columns=[student_id_col, term_col, demo_term_col])

    # Step 1: Determine the minimum 'matriculation_term' for each student
    min_matriculation_df = demographics_df.groupby(student_id_col)[term_col].min().reset_index()

    # Step 2: Merge this minimum matriculation back with the original DataFrame
    merged_df = pd.merge(demographics_df, min_matriculation_df, on=student_id_col, suffixes=('', '_min')).copy()

    # Step 3: Check for matching course terms
    merged_df['is_valid'] = merged_df[demo_term_col] == merged_df[f'{term_col}_min']

    # Step 4: Identify students with at least one valid course term match
    valid_student_ids = merged_df[merged_df['is_valid']][student_id_col].unique()

    # Step 5: Keep all rows in merged_df for students who have at least one valid match
    cleaned_df = merged_df[merged_df[student_id_col].isin(valid_student_ids)]

    return cleaned_df


def clean_and_adjust_matriculation(demographics_df, student_id_col='student_ID', matriculation_term_col='matriculation_term',
                                   demo_term_col='demographics_term', include_multiple_matriculations=0,
                                   demographics_range_min=None):
    """
    Adjusts matriculation terms to align with available demographic data.

    This function supports filtering out students with inconsistent matriculation data, ensuring that the adjusted
    matriculation term reflects either:
    - the official matriculation term (if demographic data exists for it), or
    - the earliest available demographics term.

    Parameters
    ----------
    demographics_df : pd.DataFrame
        A dataframe with one row per student per term containing both matriculation and demographic terms.
    student_id_col : str
        Column name for student ID (default = 'student_ID').
    matriculation_term_col : str
        Column name for original matriculation term (default = 'matriculation_term').
    demo_term_col : str
        Column name for demographics term (default = 'demographics_term').
    include_multiple_matriculations : int
        - 0: Exclude students with multiple distinct matriculation terms (default).
        - 1: Include all students regardless of multiple matriculation terms.
    demographics_range_min : int or None
        Optional term code. Students with `matriculation_term_min` before this value will be excluded.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        - `matriculation_term_min`: minimum matriculation term per student.
        - `earliest_demographics_term`: earliest demographics term per student.
        - `matriculation_term_adjusted`: final adjusted matriculation term used for analyses.
    """

    demographics_df = demographics_df.copy()
    validate_columns(demographics_df.columns, required_columns=[student_id_col, matriculation_term_col, demo_term_col])

    # Filter students based on the count of unique matriculation terms, if required
    matriculation_counts = demographics_df.groupby(student_id_col)[matriculation_term_col].nunique()
    if include_multiple_matriculations == 0:
        valid_student_ids = matriculation_counts[matriculation_counts == 1].index
        demographics_df = demographics_df[demographics_df[student_id_col].isin(valid_student_ids)]

    # Get the minimum matriculation term for each student
    min_matriculation_df = demographics_df.groupby(student_id_col)[matriculation_term_col].min().reset_index()
    min_matriculation_df.rename(columns={matriculation_term_col: 'matriculation_term_min'}, inplace=True)
    merged_df = pd.merge(demographics_df, min_matriculation_df, on=student_id_col, how='left')

    # If a minimum term is indicated for demographics_range_min, then filter out rows where matriculation occurred
    # before demographics_range_min
    if demographics_range_min:
        merged_df = merged_df[merged_df['matriculation_term_min'] >= demographics_range_min]
        # merged_df is now the filtered dataset

    # Determine the earliest demographics term for each student and add new column to merged_df
    earliest_demographics_df = merged_df.groupby(student_id_col)[demo_term_col].min().reset_index()
    earliest_demographics_df.rename(columns={demo_term_col: 'earliest_demographics_term'}, inplace=True)
    merged_df = pd.merge(merged_df, earliest_demographics_df, on=student_id_col, how='left')

    # Assign the adjusted matriculation term
    merged_df['matriculation_term_adjusted'] = merged_df.apply(
        lambda x: x['matriculation_term_min'] if x['earliest_demographics_term'] == x['matriculation_term_min']
        else x['earliest_demographics_term'], axis=1
    )

    return merged_df
