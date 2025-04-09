import pandas as pd
from institutionaldata.utils.validation import validate_columns

#  CAUTION: BANNER may not reliably report 'matriculation_term' do to wide variations in timing and programs in an institution
#  If you are using matriculation term values derived from BANNER, ensure that values match what you expect. Be diligent
#  about clarifying if any matriculation terms or dates are associated with the program of interest. It may be best to
#  create a new column in your dataset representing term_earliest (for a specific program). This can be done by using the
#  earliest term a student took classes. The benefit of this is avoiding situations where a student matriculates in an earlier
#  semester than they begin taking classes.

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
