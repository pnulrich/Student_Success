"""
Hazard analysis utilities for modeling student progression and retention.

This module provides functions to filter and preprocess student records,
assign outcome indicators, aggregate course load statistics, and compute
hazard-style probabilities of leaving, graduating, or changing majors.
It also includes methods to fit logistic models to cumulative outcome
probabilities for survival-style analysis.

Functions
---------
- prepare_hazard_data :
    Filter and prepare student-level records for hazard analysis based on
    major, transfer credits, start term, and academic year range.
- assign_outcome_indicators :
    Assign coded indicators (-1, 1–4) per term to represent continuation,
    leaving, graduation, or major change.
- prepare_and_process_data :
    Combine student and coursework data, assign outcome indicators, and
    compute course load metrics and summary statistics for the target major.
- calculate_probabilities :
    Derive per-semester proportions, cumulative probabilities, and active
    student counts under a hazard modeling framework.
- extract_logistic_features :
    Fit logistic curves to cumulative outcome probabilities and extract
    interpretable growth parameters (K, r, t_half).

Notes
-----
- Outcome indicator coding:
    - -1 : Continued in same major (active).
    -  1 : Left institution (inactivity ≥2 terms, no graduation).
    -  2 : Graduated in first major.
    -  3 : Graduated in different major.
    -  4 : Changed major (first occurrence flagged).
- Requires term-normalized data with consistent fields:
  ``student_ID``, ``semester_number``, ``term_earliest``, ``major_term``,
  ``major_term_earliest``, and graduation/transfer flags.
- Functions integrate with validation helpers from `utils.validation`
  and classification logic from `metrics.flagging`.
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from student_success.utils.validation import validate_columns, safe_parse_tuple
from student_success.utils.time_utils import calculate_semester_interval
from student_success.metrics.flagging import (
    classify_graduation_term,
    classify_graduation_in_first_major
)


def prepare_hazard_data(df,
                        target_major,
                        transfer_credit_max=30,
                        transfer_credit_min=0,
                        fall_start=1,
                        academic_year_min=None,
                        academic_year_max=None):
    """
    Prepares and filters student data for hazard analysis.

    This function filters students based on their earliest declared major,
    transfer credit range, earliest term, and optionally their start in a fall term.
    Additionally, it can restrict the dataset based on a range of academic years.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing student records. Required columns:
        - 'major_term_earliest': The earliest major declared by the student.
        - 'transfer_hours_term': Transfer credit hours earned by the student.
        - 'demographics_term': The term for the student's demographic record.
        - 'term_earliest': The earliest term the student enrolled.
        - 'academic_year': The academic year associated with the term.
        - 'student_ID': A unique identifier for each student.

    target_major : str
        The target major to filter students by, based on their earliest declared major.

    transfer_credit_max : int, optional
        The maximum number of transfer credit hours a student can have to be included
        in the dataset. Default is 30.

    transfer_credit_min : int, optional
        The minimum number of transfer credit hours a student must have to be included.
        Default is 0.

    fall_start : int, optional
        If set to 1, filters students to those whose earliest term ends with `8`,
        indicating a fall start term. If set to 0, all terms are included. Default is 1.

    academic_year_min : int, optional
        The minimum academic year to include in the filtered dataset. If None, no
        lower limit is applied. Default is None.

    academic_year_max : int, optional
        The maximum academic year to include in the filtered dataset. If None, no
        upper limit is applied. Default is None.

    Returns
    -------
    pandas.DataFrame
        A DataFrame of filtered student records meeting the specified criteria.

    Prints
    ------
    - The number of unique students meeting the transfer credit and target major criteria.
    - If `fall_start` is set to 1, the number of unique students who also started
      in a fall term.

    Notes
    -----
    - Assumes term codes ending in `8` correspond to fall semesters.
    - Designed for use in hazard analysis, focusing on student retention and progression.
    - If `academic_year_min` or `academic_year_max` are specified, filters the dataset
      to include only records within the specified academic year range.

    Examples
    --------
    >>> filtered_df = prepare_hazard_data(
    ...     df, "BIO", transfer_credit_max=30, transfer_credit_min=10,
    ...     fall_start=1, academic_year_min=2010, academic_year_max=2024
    ... )
    """

    # Confirm that essential fields are present in the input dataframe
    required_cols = ['major_term_earliest', 'transfer_hours_term', 'demographics_term', 'term_earliest',
                     'academic_year', 'student_ID']
    validate_columns(df.columns, required_cols)

    # Filter students based on criteria
    student_list = df[
        (df['major_term_earliest'] == target_major) &  # this only looks at those students starting as target_major
        (df['transfer_hours_term'].between(transfer_credit_min, transfer_credit_max, inclusive='both')) &
        (df['demographics_term'] == df['term_earliest']) &
        ((academic_year_min is None) | (df['academic_year'] >= academic_year_min)) &
        ((academic_year_max is None) | (df['academic_year'] <= academic_year_max))
        ]['student_ID'].unique()

    # Filter the main DataFrame
    filtered_df = df[df['student_ID'].isin(student_list)].copy()
    print(f"[INFO] {len(student_list)} students started in {target_major} "
          f"with {transfer_credit_min}–{transfer_credit_max} transfer credits.")

    # Further filter by Fall start if required
    if fall_start:
        filtered_df = filtered_df[filtered_df['term_earliest'] % 100 == 8].copy()
        print(f"[INFO] {filtered_df['student_ID'].nunique()} students began in Fall terms.")

    return filtered_df


def assign_outcome_indicators(student_df, max_demographics_term):
    """
    Process a student's academic data and assign outcome indicators.

    This function processes a DataFrame containing a student's academic records,
    assigning an outcome indicator for each term based on changes in major,
    graduation status, and long enrollment gaps.

    Parameters
    ----------
    student_df : pandas.DataFrame
        A DataFrame containing a student's term-by-term academic data.
        Required columns:
        - 'major_term_earliest': The student’s original declared major.
        - 'term_earliest': The student’s first term of enrollment.
        - 'semester_number': The normalized sequence of academic semesters.
        - 'major_term': The declared major during each term.
        - 'demographics_term': Term code for the current record.
        - 'flag_graduation_term': 1 if student graduates in this term; 0 otherwise.
        - Optionally: 'flag_graduated_in_first_major' (1 if graduated in original major)

    max_demographics_term : int
        The maximum term in the dataset. Used to assess potential dropouts
        based on enrollment gaps.

    Returns
    -------
    list of int
        A list of assigned outcome indicators for each row in `student_df`.
        The list is in the same order as `student_df` and can be assigned as a new column (e.g., 'outcome_indicator').

    Outcome Logic
    -------------
    - Each outcome indicator reflects what happened *after* the given term.
    - Outcome is assigned based on change between the current and previous term,
      or based on whether the term is the student’s last known semester.

    Indicators:
        - -1 : No change from prior term; student continues in same major.
        -  1 : Left the university after this term (inactivity for 2+ terms, no graduation).
        -  2 : Graduated in their original declared major in this term.
        -  3 : Graduated in a different major in this term.
        -  4 : Actively changed major in this term (compared to previous term).

    Notes
    -----
    - First term is always coded as -1 since no prior record exists.
    - Graduation and dropout are only assessed in the student’s final semester.
    - A long gap is defined as ≥2 terms without further enrollment.
    - This function supersedes earlier logic in `process_student_data()`.
    - Outcome indicator values are determined one row at a time but require knowledge of the full student history.


    Examples
    --------
    >>> student_data_df = pd.DataFrame({
    ...     'major_term_earliest': ['BIO'] * 3,
    ...     'term_earliest': [202001, 202005, 202008],
    ...     'semester_number': [1, 2, 3],
    ...     'major_term': ['BIO', 'BIO', 'CHEM'],
    ...     'demographics_term': [202001, 202005, 202008],
    ...     'flag_graduation_term': [0, 0, 0]
    ... })
    >>> assign_outcome_indicators(student_data_df, 202008)
    [-1, -1, 4]
    """

    if student_df.empty:
        return []

    required_cols = [
        'major_term_earliest',
        'term_earliest',
        'semester_number',
        'major_term',
        'demographics_term',
        'flag_graduation_term'
    ]
    validate_columns(student_df.columns, required_cols)

    # Add 'flag_graduated_in_first_major' if not already present
    if 'flag_graduated_in_first_major' not in student_df.columns:
        student_df['flag_graduated_in_first_major'] = classify_graduation_in_first_major(student_df)

    # Sort by semester_number just in case
    student_df = student_df.sort_values("semester_number").reset_index(drop=True)
    indicators = []
    num_rows = len(student_df)
    major_change_already_occurred = False

    for i, row in student_df.iterrows():
        current_sem = row['semester_number']
        current_major = row['major_term']
        graduated = row['flag_graduation_term'] == 1
        graduated_in_first_major = row['flag_graduated_in_first_major'] == 1
        is_last = i == num_rows - 1

        if is_last:
            if graduated:
                indicators.append(2 if graduated_in_first_major else 3)
            elif calculate_semester_interval(row['demographics_term'], max_demographics_term) >= 2:
                indicators.append(1)
            else:
                indicators.append(-1)
        else:
            next_major = student_df.loc[i + 1, 'major_term']
            if current_major != next_major and not major_change_already_occurred:
                indicators.append(4)  # Forward-looking major change
                major_change_already_occurred = True
            else:
                indicators.append(-1)

    return indicators


def prepare_and_process_data(student_major_data_df,
                             coursework_df,
                             target_major,
                             transfer_credit_min,
                             transfer_credit_max,
                             target_major_course_prefix,
                             academic_year_min=None,
                             academic_year_max=None):
    """
    Prepares and processes data for hazard analysis.

    This function filters, processes, and aggregates student and coursework data
    to support hazard analysis, focusing on academic progression, major changes,
    and course load statistics for a specified target major.

    Parameters
    ----------
    student_major_data_df : pandas.DataFrame
        A DataFrame containing student demographic and academic information.
        Required columns include:
        - 'student_ID': Unique identifier for students.
        - 'demographics_term': Term of demographic data.
        - 'major_term': Current major for the term.
        - 'major_graduation': Graduation status or term.
        - 'semester_number': Sequential outcome indicator.
        - 'term_earliest': Earliest term of enrollment.

    coursework_df : pandas.DataFrame
        A DataFrame containing detailed course information.
        Required columns include:
        - 'student_ID': Unique identifier for students.
        - 'course_prefix': Prefix of the course (e.g., 'BIO').
        - 'course_credits': Credit hours for each course.
        - 'demographics_term': Term in which the course was taken.

    target_major : str
        The target major to filter and analyze (e.g., 'BIO').

    transfer_credit_min : int
        Minimum number of transfer credit hours allowed for students
        to be included in the analysis.

    transfer_credit_max : int
        Maximum number of transfer credit hours allowed for students
        to be included in the analysis.

    target_major_course_prefix : str
        The course prefix associated with the target major (e.g., 'BIOL').

    academic_year_min : int, optional (e.g., 2018, YYYY)
        The minimum academic year to include in the analysis. If None, no
        lower limit is applied.

    academic_year_max : int, optional (e.g., 2018, YYYY)
        The maximum academic year to include in the analysis. If None, no
        upper limit is applied.

    Returns
    -------
    tuple
        - filtered_df (pandas.DataFrame): All terms for students who met inclusion criteria
          with outcome indicators and course metrics merged in.
        - target_major_courseload_df (pandas.DataFrame): Summary statistics
          of target major course load by semester, including mean and standard
          deviation for course credits and course counts.

    Notes
    -----
    - Filters students based on target major, transfer credit limits, and fall-term starts.
    - Assigns outcome indicators to track progression, major changes, gaps in enrollment, and graduation status. Only the first major change is flagged.
    - Aggregates course load data for the target major, calculating:
        - Number of courses taken per semester.
        - Total credits earned per semester.
        - Summary statistics (mean and standard deviation) for course credits and course counts by semester.
    - Assumes terms ending with '8' correspond to fall semesters.
    - Filters and processes coursework data to focus only on the target major.
    - Outcome indicators are assigned on a per-student, per-semester basis.
    - Only the first instance of a major change (outcome 4) is retained; subsequent major changes are reset to -1 (no change).

    Examples
    --------
    >>> filtered_data_df, stats_df = prepare_and_process_data(
    ...     student_major_data_df, coursework_df, "BIO", 30, "BIOL", 2010, 2024
    ... )
    >>> print(filtered_data_df.head())
    >>> print(stats_df)
    """

    required_student_cols = [
        'major_term_earliest',
        'transfer_hours_term',
        'demographics_term',
        'term_earliest',
        'academic_year',
        'student_ID',
        'major_term',
        'major_graduation',
        'semester_number'
    ]

    required_coursework_cols = [
        'student_ID',
        'course_prefix',
        'course_credits',
        'course_number',
        'course_suffix',
        'demographics_term'
    ]

    validate_columns(student_major_data_df.columns, required_student_cols)
    validate_columns(coursework_df.columns, required_coursework_cols)

    # Filter student data based on arguments passed to function
    filtered_df = prepare_hazard_data(
        df=student_major_data_df,
        target_major=target_major,
        transfer_credit_min=transfer_credit_min,
        transfer_credit_max=transfer_credit_max,
        fall_start=1,  # Include only students who started in fall terms
        academic_year_min=academic_year_min,
        academic_year_max=academic_year_max
    )

    # Normalize major_graduation to parsed tuples
    filtered_df['major_graduation'] = filtered_df['major_graduation'].apply(safe_parse_tuple)

    # Compute graduation flags
    filtered_df['flag_graduation_term'] = classify_graduation_term(filtered_df)
    if 'flag_graduated_in_first_major' not in filtered_df.columns:
        filtered_df['flag_graduated_in_first_major'] = classify_graduation_in_first_major(filtered_df)

    # Identify the latest term in the dataset for reference in processing
    max_demographics_term = filtered_df['demographics_term'].max()

    # Assign outcome indicators to track student status by semester
    filtered_df = (
        filtered_df.groupby('student_ID', group_keys=False)
        .apply(lambda x: x.assign(
            outcome_indicator=assign_outcome_indicators(x.sort_values('semester_number'), max_demographics_term)
        ))
    )

    # Ensure only the first major change is flagged as 4
    # Identify the earliest major change for each student and set all subsequent major changes to -1
    filtered_df['earliest_major_change'] = (
        filtered_df[filtered_df['outcome_indicator'] == 4]
        .groupby('student_ID')['semester_number']
        .transform('min')
    )

    filtered_df['outcome_indicator_original'] = filtered_df['outcome_indicator']

    filtered_df['outcome_indicator'] = filtered_df.apply(
        lambda current_row: -1 if current_row['outcome_indicator'] == 4 and current_row['semester_number'] !=
                                  current_row['earliest_major_change']
        else current_row['outcome_indicator'],
        axis=1
    )
    # Drop helper column
    filtered_df.drop(columns=['earliest_major_change'], inplace=True)

    # Filter coursework to include only courses in the target major
    filtered_coursework_df = coursework_df.copy()
    filtered_coursework_df = filtered_coursework_df[
        filtered_coursework_df['course_prefix'] == target_major_course_prefix
        ].copy()

    # Create full course number codes (e.g., BIOL1104K)
    filtered_coursework_df['course_fullcode'] = (
            filtered_coursework_df['course_prefix'] +
            filtered_coursework_df['course_number'].astype(str) +
            filtered_coursework_df['course_suffix'].fillna('')
    )

    # Aggregate course load metrics (number of courses, total credits, course list) by semester
    result = filtered_coursework_df.groupby(['student_ID', 'demographics_term']).agg(
        semester_courses_target_major=('course_prefix', 'count'),
        semester_credits_target_major=('course_credits', 'sum'),
        course_list=('course_fullcode', list)
    ).reset_index()

    # Merge course load data into the filtered student DataFrame
    filtered_df = filtered_df.merge(result, on=['student_ID', 'demographics_term'], how='left')
    filtered_df['semester_courses_target_major'] = filtered_df['semester_courses_target_major'].fillna(0)
    filtered_df['semester_credits_target_major'] = filtered_df['semester_credits_target_major'].fillna(0)

    # Calculate descriptive statistics for credit hours by semester
    # TODO: Assess how this will be impacted by anyone one who changed out of the target major but took target major courses after changing
    credits_stats = (
        filtered_df[
            (filtered_df['outcome_indicator'] == -1) &
            (filtered_df['major_term'] == target_major)
            ]
        .groupby('semester_number')
        .agg(
            avg_semester_credits_target_major=('semester_credits_target_major', 'mean'),
            std_semester_credits_target_major=('semester_credits_target_major', 'std')
        )
        .reset_index()
    )

    # Calculate descriptive statistics for course counts by semester
    courses_stats = (
        filtered_df[
            (filtered_df['outcome_indicator'] == -1) &
            (filtered_df['major_term'] == target_major)
            ]
        .groupby('semester_number')
        .agg(
            avg_semester_courses_target_major=('semester_courses_target_major', 'mean'),
            std_semester_courses_target_major=('semester_courses_target_major', 'std')
        )
        .reset_index()
    )

    # Combine credit and course statistics into a single DataFrame
    target_major_courseload_df = pd.merge(
        credits_stats, courses_stats, on='semester_number', how='inner'
    )

    return filtered_df, target_major_courseload_df


def calculate_probabilities(input_df):
    """
    Calculate proportions, cumulative probabilities, and active student counts by semester.

    This function computes:
    1. Proportions of students by `outcome_indicator` for each semester using a hazard-based method.
       - Outcome 4 (Changed Major) is modeled as a forward-looking risk:
         students are flagged if they change majors in the *next* semester,
         and the probability is normalized to the number of students *active in the current semester*.
       - Outcomes 1, 2, 3, and -1 are normalized to the active student population in the *current* semester.
    2. Cumulative probabilities for each outcome, assuming students begin fully active (100%).
    3. Total active student counts per semester.
    4. A filtered DataFrame excluding rows with `outcome_indicator == -1` to focus on terminal or transition outcomes.

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame containing student-level outcome data. Required columns:
        - 'semester_number': Integer identifier for the term of enrollment.
        - 'outcome_indicator': Coded outcome for the semester. Expected values:
            - -1 = Active (no terminal or transition outcome yet)
            -  1 = Left College
            -  2 = Graduated in Target Major
            -  3 = Graduated in Other Major
            -  4 = Changed Major
        - 'student_ID': Unique student identifier.

    Returns
    -------
    dict
        Dictionary containing:
        - "proportions_df": pandas.DataFrame
            Proportion of students with each outcome per semester.
        - "cumulative_df": pandas.DataFrame
            Cumulative probabilities of each outcome assuming 100% start active.
        - "active_student_counts": pandas.Series
            Number of active students per semester (based on input data).
        - "masked_df": pandas.DataFrame
            Subset of input_df where `outcome_indicator != -1`.

    Notes
    -----
    - This function reflects a hazard framework: students at risk of each outcome are only those still active.
    - The probability of changing majors is derived based on changes observed in the *next* semester.
    - Graduation and leaving college are treated as terminal events within the semester and normalized to the current active base.
    - The cumulative probability table is useful for generating survival-style plots across semesters.

    Examples
    --------
    >>> result = calculate_probabilities(student_df)
    >>> result["proportions_df"].head()
    >>> result["cumulative_df"].head()
    >>> result["active_student_counts"]
    >>> result["masked_df"].head()
    """

    required_input_cols = ['semester_number', 'outcome_indicator', 'student_ID']
    validate_columns(input_df.columns, required_input_cols)

    # Sort and prepare
    input_df = input_df.sort_values(['student_ID', 'semester_number'])

    # Get active counts per semester
    active_student_counts = input_df.groupby("semester_number")["student_ID"].nunique()

    # Initialize output DataFrame
    semesters = sorted(input_df["semester_number"].unique())
    proportions_records = []

    for idx, sem in enumerate(semesters):
        df_curr = input_df[input_df["semester_number"] == sem]
        total_curr = len(df_curr)

        # For current semester, compute:
        # - graduates in-major (2), graduates other (3), left college (1)
        grad_in_major = (df_curr["outcome_indicator"] == 2).sum()
        grad_other = (df_curr["outcome_indicator"] == 3).sum()
        left_college = (df_curr["outcome_indicator"] == 1).sum()

        if sem < max(semesters):
            next_sem = sem + 1
            # Students who changed major in next semester
            next_changers = input_df[
                (input_df["semester_number"] == next_sem) &
                (input_df["outcome_indicator"] == 4)
                ]["student_ID"].unique()

            # Students active in current semester
            active_now = set(input_df[
                                 (input_df["semester_number"] == sem) &
                                 (input_df["outcome_indicator"] == -1)
                                 ]["student_ID"].unique())

            changed_major = len(set(next_changers).intersection(active_now))
            curr_active_count = len(active_now)
        else:
            changed_major = 0
            curr_active_count = 1  # avoid divide-by-zero

        proportions_records.append({
            "semester_number": sem,
            1: left_college / total_curr if total_curr else 0,
            2: grad_in_major / total_curr if total_curr else 0,
            3: grad_other / total_curr if total_curr else 0,
            4: changed_major / curr_active_count if curr_active_count else 0,
            -1: (df_curr["outcome_indicator"] == -1).sum() / total_curr if total_curr else 0
        })

    proportions_df = pd.DataFrame(proportions_records)

    # Cumulative calculations
    cumulative_df = proportions_df[["semester_number"]].copy()
    active_population = 1.0  # Start with 100% of the population active
    cumulative_outcomes = {1: [], 2: [], 3: [], 4: []}

    for _, row in proportions_df.iterrows():
        for col in [1, 4, 2, 3]:
            current_prob = row.get(col, 0) * active_population
            if not cumulative_outcomes[col]:
                cumulative_outcomes[col].append(current_prob)
            else:
                cumulative_outcomes[col].append(cumulative_outcomes[col][-1] + current_prob)
        active_population *= (row.get(-1, 0) + row.get(4, 0))

    # Calculate -1 as the remaining active population
    cumulative_outcomes[-1] = [
        1.0 - (cumulative_outcomes[1][i] + cumulative_outcomes[2][i] + cumulative_outcomes[3][i])
        for i in range(len(proportions_df))
    ]

    for col in cumulative_outcomes:
        cumulative_df[col] = cumulative_outcomes[col]

    masked_df = input_df[input_df["outcome_indicator"] != -1].copy()

    return {
        "proportions_df": proportions_df,
        "cumulative_df": cumulative_df,
        "active_student_counts": active_student_counts,
        "masked_df": masked_df
    }


def extract_logistic_features(outcome_indicator, semester_numbers, cumulative_probabilities):
    """
    Fit a logistic model and extract features.

    Parameters
    ----------
    outcome_indicator : int
        outcome indicator code
        - -1 : No change from the previous term
        - 1  : Left university
        - 2  : Graduated in first major
        - 3  : Graduated in different major
        - 4  : Changed to different major (still active)
    semester_numbers : array-like
        The semester numbers.
    cumulative_probabilities : array-like
        The cumulative probabilities for a given outcome.

    Returns
    -------
    dict
        A dictionary containing the logistic model parameters:
        - "K": Maximum cumulative probability
        - "r": Growth rate
        - "t_half": Half-max semester number
    """

    def logistic_function(t, K, r, t_half):
        return K / (1 + np.exp(-r * (t - t_half)))

    # Fit the logistic model
    params, _ = curve_fit(logistic_function, semester_numbers, cumulative_probabilities, maxfev=10000)

    # Extract parameters
    K, r, t_half = params
    return {"Outcome": outcome_indicator, "K": K, "r": r, "t_half": t_half}
