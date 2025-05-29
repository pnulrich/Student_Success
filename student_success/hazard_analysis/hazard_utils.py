import ast
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from student_success.utils.validation import validate_columns

def prepare_hazard_data(df,
                        target_major,
                        transfer_credit_max=30,
                        transfer_credit_min=0,
                        fall_start=1,
                        academic_year_min = None,
                        academic_year_max = None):
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
    Number of unique students in BIO with transfer credits from 10 to as many as 30: 100
    Number of unique students in BIO with transfer credits from 10 to as many as 30 with Fall start: 75
    """

    #  Confirm that essential fields are present in the input dataframe
    required_cols = ['major_term_earliest', 'transfer_hours_term', 'demographics_term', 'term_earliest',
                         'academic_year', 'student_ID']
    validate_columns(df.columns, required_cols)


    # Filter students based on criteria
    student_list = df[
        (df['major_term_earliest'] == target_major) & # this only looks at those students starting as target_major
        (df['transfer_hours_term'].between(transfer_credit_min, transfer_credit_max, inclusive='both')) &
        (df['demographics_term'] == df['term_earliest']) &
        ((academic_year_min is None) | (df['academic_year'] >= academic_year_min)) &
        ((academic_year_max is None) | (df['academic_year'] <= academic_year_max))
        ]['student_ID'].unique()


    # Filter the main DataFrame
    filtered_df = df[df['student_ID'].isin(student_list)].copy()
    print(
        f"Number of unique students in {target_major} with {transfer_credit_min} to {transfer_credit_max} transfer credits: {filtered_df['student_ID'].nunique()}")

    # Further filter by Fall start if required
    if fall_start:
        filtered_df = filtered_df[filtered_df['term_earliest'] % 100 == 8].copy()
        print(
            f"Number of unique students in {target_major} with {transfer_credit_min} to {transfer_credit_max} transfer credits with Fall start: {filtered_df['student_ID'].nunique()}")

    return filtered_df


def calculate_semester_interval(current_term, max_term):
    """
    Calculate the number of academic semesters between current_term and max_term.

    This function assumes a forward academic sequence: Spring (01), Summer (05), Fall (08).
    It raises an error if current_term is after max_term.

    Parameters
    ----------
    current_term : int
        The starting term code in format YYYYMM.
    max_term : int
        The ending term code in format YYYYMM.

    Returns
    -------
    int
        The number of semesters between current_term and max_term.

    Raises
    ------
    ValueError
        If current_term is later than max_term.

    Examples
    --------
    >>> calculate_semester_interval(202308, 202401)
    1
    >>> calculate_semester_interval(202308, 202405)
    2
    >>> calculate_semester_interval(202308, 202305)
    ValueError: current_term (202308) must not be after max_term (202305)
    """

    if current_term > max_term:
        raise ValueError(f"current_term ({current_term}) must not be after max_term ({max_term})")


    # Semester sequence within academic year: Fall (08), Spring (01), Summer (05)
    semester_sequence = ['08', '01', '05']

    current_year = int(str(current_term)[:4])
    current_semester = str(current_term)[4:]
    max_year = int(str(max_term)[:4])
    max_semester = str(max_term)[4:]

    # Adjust year for Fall semester
    if current_semester == '08':
        current_year += 1
    if max_semester == '08':
        max_year += 1

    # Calculate total semesters missed
    semesters_missed = 0

    # Start from the current semester's position
    next_semester_index = semester_sequence.index(current_semester)
    checking_year = current_year

    while True:
        # Move to next semester in sequence
        next_semester_index = (next_semester_index + 1) % 3

        # If we've completed the sequence and are starting a new year
        if next_semester_index == 0:
            checking_year += 1

        # Adjust year back if we're constructing a Fall term
        if semester_sequence[next_semester_index] == '08':
            term_year = checking_year - 1

        else:
            term_year = checking_year

        # Construct the next term to check
        next_term = int(f"{term_year}{semester_sequence[next_semester_index]}")

        # Stop if we've reached or exceeded the max term
        if next_term > max_term:
            break

        # Increment missed semesters
        semesters_missed += 1

    return semesters_missed


def assign_outcome_indicators(row, prev_major_term, term_earliest, first_major, is_last_semester,
                               max_demographics_term):
    """
    Assign an outcome indicator based on a student's term history.

    This function assigns an indicator representing a student's academic
    status in a given term based on their academic history. It considers
    major changes, long enrollment gaps, and graduation status.

    Parameters
    ----------
    row : pandas.Series
        A row from the student's DataFrame representing a specific term.
    prev_major_term : str or int
        The student's previous major term.
    term_earliest : int
        The student's earliest term of enrollment.
    first_major : str
        The student's first declared major.
    is_last_semester : bool
        Whether the current row is the student's last semester in the dataset.
    max_demographics_term : int
        The maximum demographic term code in the dataset.

    Returns
    -------
    int
        outcome indicator code:
        - -1 : No change from the previous term
        - 1  : Left the university
        - 2  : Graduated in the first major
        - 3  : Graduated in a different major
        - 4  : Changed to a different major (still active)

    Notes
    -----
    - Assumes that Fall terms are indicated by a semester code ending in `08`.
    - Gaps longer than 2 terms are considered long absences.
    - Graduation is determined based on the `flag_graduation_term` and
      `major_graduation` fields.
    - 'first_major' is extracted from the earliest term and represents the student's original, declared major.
    - This function should be used within 'process_student_data()'. This ensures that 'first_major' is correctly derived.


    Examples
    --------
    >>> inner_row = {
    ...     'demographics_term': 202308,
    ...     'flag_graduation_term': 1,
    ...     'major_graduation': 'BIO'
    ... }
    >>> assign_outcome_indicators(row, 202208, 202001, 'BIO', True, 202401)
    2
    """

    # Check if the student has missed multiple consecutive semesters
    def has_long_gap(current_term, max_term, gap_threshold=2):
        return calculate_semester_interval(current_term, max_term) >= gap_threshold

    # Check if this is the last semester in the available data
    is_last_available_semester = row['demographics_term'] == max_demographics_term

    # Address a student's last semester status
    if is_last_semester:
        if row['flag_graduation_term'] == 1:
            if row['major_graduation'][0] == first_major:
                return 2  # Graduated in the first major
            else:
                return 3  # Graduated in a different major

        # If the row represents a student's last semester, student does not graduate, and there is a long gap, then mark student as having left college
        elif has_long_gap(current_term=row['demographics_term'], max_term=max_demographics_term):
            return 1

    # When a term is equivalent ot the last term code in the dataset, check if student has a long gap
    if is_last_available_semester:
        if row['demographics_term'] == term_earliest:
            return -1  # if the last term in the dataset is the student's first semester, then leave unchanged
        elif row['major_term'] == prev_major_term and not has_long_gap(current_term=row['demographics_term'],
                                                                       max_term=max_demographics_term):
            return -1  # Major unchanged from prior semester and no long gap
        elif row['major_term'] != prev_major_term and not has_long_gap(current_term=row['demographics_term'],
                                                                       max_term=max_demographics_term):
            return 4  # major changed from prior semester and no long gap

    # For the earliest term in a student's record, set all values to -1
    elif row['demographics_term'] == term_earliest:
        return -1

        # For all other terms,
    elif row['major_term'] != prev_major_term:
        return 4  # Left the major
    else:
        return -1  # No specific change (edge case)


# Process each student's data
def process_student_data(student_df, max_demographics_term):
    """
    Process a student's academic data and assign outcome indicators.

    This function processes a DataFrame containing a student's academic records,
    assigning a outcome indicator for each term based on enrollment history,
    major changes, graduation status, and enrollment gaps.

    Parameters
    ----------
    student_df : pandas.DataFrame
        A DataFrame containing a student's term-by-term academic data.
        Required columns:
        - 'major_term_earliest'
        - 'term_earliest'
        - 'semester_number'
        - 'major_term'
        - 'demographics_term'
    max_demographics_term : int
        The maximum demographic term code in the dataset.

    Returns
    -------
    list of int
        A list of assigned outcome indicators for each row in `student_df`.

    Notes
    -----
    - Tracks major changes by comparing `major_term` between terms.
    - Considers gaps longer than 2 terms as a break in enrollment.
    - Assigns indicators:
        - -1 : No change from previous term
        - 1  : Left the university
        - 2  : Graduated in the first major
        - 3  : Graduated in a different major
        - 4  : Changed to a different major (still active)

    Examples
    --------
    >>> student_data_df = pd.DataFrame({
    ...     'major_term_earliest': ['BIO'] * 3,
    ...     'term_earliest': [202001, 202005, 202008],
    ...     'semester_number': [1, 2, 3],
    ...     'major_term': ['BIO', 'BIO', 'CHEM'],
    ...     'demographics_term': [202001, 202005, 202008]
    ... })
    >>> process_student_data(student_data_df, 202008)
    [-1, -1, 4]
    """

    required_student_cols = ['major_term_earliest', 'term_earliest', 'semester_number', 'major_term', 'demographics_term']
    validate_columns(student_df, required_student_cols)

    first_major = student_df.iloc[0]['major_term_earliest']  # First major
    term_earliest = student_df['term_earliest'].min()  # earliest semester code
    last_semester_number = student_df['semester_number'].max()  # Last semester number
    prev_major_term = None  # Track the previous semester's major
    # max_demographics_term = student_df['demographics_term'].max()
    # print("Max demographics term = ", max_demographics_term)
    indicators = []
    for i, row in student_df.iterrows():
        is_last_semester = row['semester_number'] == last_semester_number
        indicator = assign_outcome_indicators(row, prev_major_term, term_earliest, first_major, is_last_semester,
                                               max_demographics_term)
        indicators.append(indicator)
        prev_major_term = row['major_term']

    return indicators


# convert major_graduation to a tuple (WHY DID I ENCODE major_graduation as a string in the first place?)
def safe_eval(value):
    """
    Safely evaluate a string containing a Python literal expression.

    This function attempts to evaluate a string representation of a Python literal (e.g., lists, dictionaries,
    integers, floats, booleans). If the input is not a string, it is returned unchanged. If evaluation fails due to
    invalid syntax or a value error, the function returns `None`.

    Parameters
    ----------
    value : str or any
        The input value to be evaluated. If `value` is a string containing a valid Python literal expression, it is
        evaluated using `ast.literal_eval`. Non-string inputs are returned as is.

    Returns
    -------
    any
        The evaluated Python object if the input is a valid Python literal string. Non-string inputs are returned
        unchanged. If evaluation fails, `None` is returned.

    Notes
    -----
    - This function uses `ast.literal_eval`, which is safer than `eval` as it only evaluates Python literal expressions.
    - Common use cases include converting strings like "{'key': 'value'}" or "[1, 2, 3]" into Python objects.

    Examples
    --------
    >>> safe_eval("{'key': 'value'}")
    {'key': 'value'}

    >>> safe_eval("[1, 2, 3]")
    [1, 2, 3]

    >>> safe_eval(42)
    42  # Non-string input is returned as is

    >>> safe_eval("invalid syntax")
    None  # Invalid string returns None
    """
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except (ValueError, SyntaxError):
        return None  # Or handle in a way appropriate to your use case


def prepare_and_process_data(student_major_data_df,
                             coursework_df,
                             target_major,
                             transfer_credit_min,
                             transfer_credit_max,
                             target_major_course_prefix,
                             academic_year_min = None,
                             academic_year_max = None):
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

    transfer_credit_max : int
        Maximum number of transfer credit hours allowed for students
        to be included in the analysis.

    target_major_course_prefix : str
        The course prefix associated with the target major (e.g., 'BIO').

    academic_year_min : int, optional
        The minimum academic year to include in the analysis. If None, no
        lower limit is applied.

    academic_year_max : int, optional
        The maximum academic year to include in the analysis. If None, no
        upper limit is applied.

    Returns
    -------
    tuple
        - filtered_df (pandas.DataFrame): Filtered and processed student data
          with added outcome indicators and course load information.
        - target_major_courseload_df (pandas.DataFrame): Summary statistics
          of target major course load by semester, including mean and standard
          deviation for course credits and course counts.

    Notes
    -----
    - Filters students based on target major, transfer credit limits, and fall-term starts.
    - Assigns outcome indicators to track progression, major changes, gaps in enrollment,
      and graduation status. Only the first major change is flagged.
    - Aggregates course load data for the target major, calculating:
      - Number of courses taken per semester.
      - Total credits earned per semester.
      - Summary statistics (mean and standard deviation) for course credits
        and course counts by semester.
    - Assumes terms ending with '8' correspond to fall semesters.
    - Filters and processes coursework data to focus only on the target major.

    Examples
    --------
    >>> filtered_data_df, stats_df = prepare_and_process_data(
    ...     student_major_data_df, coursework_df, "BIO", 30, "BIO", 2010, 2024
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
        academic_year_min = academic_year_min,
        academic_year_max = academic_year_max
    )


    # filtered_df = fil`tered_df[filtered_df['major_term'] == target_major].copy()

    print(filtered_df['major_term'].unique())

    # Convert 'major_graduation' strings to Python objects (e.g., tuples) for processing
    filtered_df['major_graduation'] = filtered_df['major_graduation'].apply(safe_eval)

    # Identify the latest term in the dataset for reference in processing
    max_demographics_term = filtered_df['demographics_term'].max()

    # Assign outcome indicators to track student status by semester
    outcome_indicators_dict = (
        filtered_df.groupby('student_ID')
        .apply(lambda x: process_student_data(x.sort_values('semester_number'), max_demographics_term))
        .to_dict()  # Convert the grouped results into a dictionary
    )

    # Map outcome indicators back to the main DataFrame
    indicators = []
    for _, row in filtered_df.iterrows():
        student_id = row['student_ID']
        student_group = filtered_df[filtered_df['student_ID'] == student_id]  # Group data by student
        student_group_sorted = student_group.sort_values('semester_number')  # Sort by semester
        row_index = student_group_sorted.index.get_loc(_)  # Find the row index for the current term
        indicator = outcome_indicators_dict[student_id][row_index]  # Retrieve the indicator
        indicators.append(indicator)

    # Add the computed outcome indicators to the DataFrame
    filtered_df['outcome_indicator'] = indicators

    # Ensure only the first major change is flagged as 4
    # Identify the earliest major change for each student and set all subsequent major changes to -1
    filtered_df['earliest_major_change'] = (
        filtered_df[filtered_df['outcome_indicator'] == 4]
        .groupby('student_ID')['semester_number']
        .transform('min')
    )
    filtered_df['outcome_indicator'] = filtered_df.apply(
        lambda current_row: -1 if current_row['outcome_indicator'] == 4 and current_row['semester_number'] != current_row['earliest_major_change'] else current_row['outcome_indicator'],
        axis=1
    )
    # Drop helper column
    filtered_df.drop(columns=['earliest_major_change'], inplace=True)



    # Calculate course load statistics for the target major
    filtered_coursework_df = coursework_df.copy()

    # Filter coursework to include only courses in the target major
    filtered_coursework_df = filtered_coursework_df[filtered_coursework_df['course_prefix'] == target_major_course_prefix].copy()

    # create full course number codes
    filtered_coursework_df['course_fullcode'] = filtered_coursework_df['course_prefix'] + filtered_coursework_df['course_number'].astype(
        str) + filtered_coursework_df['course_suffix'].fillna('')

    # Aggregate course load metrics (number of courses, total credits, course list) by semester
    result = filtered_coursework_df.groupby(['student_ID', 'demographics_term']).agg(
        semester_courses_target_major=('course_prefix', 'count'),
        semester_credits_target_major=('course_credits', 'sum'),
        course_list=('course_fullcode', list)  # Collect a list of courses taken
    ).reset_index()

    # Merge course load data into the filtered student DataFrame
    filtered_df = filtered_df.merge(result, on=['student_ID', 'demographics_term'], how='left')
    filtered_df['semester_courses_target_major'] = filtered_df['semester_courses_target_major'].fillna(0)
    filtered_df['semester_credits_target_major'] = filtered_df['semester_credits_target_major'].fillna(0)

    # Calculate descriptive statistics for credit hours by semester
    credits_stats = (
        filtered_df[
            (filtered_df['outcome_indicator'] == -1) &  # Focus on active students
            (filtered_df['major_term'] == target_major)  # Students still in the target major
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
            (filtered_df['outcome_indicator'] == -1) &  # Focus on active students
            (filtered_df['major_term'] == target_major)  # Students still in the target major
        ]
        .groupby('semester_number')
        .agg(
            avg_semester_courses_target_major=('semester_courses_target_major', 'mean'),
            std_semester_courses_target_major=('semester_courses_target_major', 'std'),
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
    1. Proportions of students by `outcome_indicator` for each semester.
    2. Cumulative probabilities of various outcomes, adjusted for the active population.
    3. Total active student counts per semester.
    4. A filtered DataFrame (`masked_df`) excluding rows with inactive status (`outcome_indicator == -1`).

    Parameters
    ----------
    input_df : pandas.DataFrame
        A DataFrame containing student data with the following required columns:
        - 'semester_number': Identifier for the semester.
        - 'outcome_indicator': Outcome indicator for each student.
        - 'student_ID': Unique identifier for students.

    Returns
    -------
    dict
        A dictionary containing:
        - "proportions_df": pandas.DataFrame
            Proportions of each outcome (`outcome_indicator`) by semester.
        - "cumulative_df": pandas.DataFrame
            Cumulative probabilities for each outcome by semester.
        - "active_student_counts": pandas.Series
            Total number of active students per semester.
        - "masked_df": pandas.DataFrame
            Filtered DataFrame excluding rows with `outcome_indicator == -1`.

    Notes
    -----
    - The function assumes that outcomes are represented by specific values of `outcome_indicator`.
    - Cumulative probabilities are calculated for each outcome in the following order:
      1 (Left College), 4 (Changed Major), 2 (Graduated in Target Major), 3 (Graduated Other).
    - Active student counts are used to normalize proportions.

    Examples
    --------
    >>> result = calculate_probabilities(student_df)
    >>> print(result["proportions_df"].head())
    >>> print(result["cumulative_df"].head())
    >>> print(result["active_student_counts"])
    >>> print(result["masked_df"].head())
    """

    required_input_cols = ['semester_number', 'outcome_indicator', 'student_ID']
    validate_columns(required_input_cols, required_input_cols)

    # Calculate the proportions of active students by semester and status
    proportions_df = (
        input_df.groupby("semester_number")["outcome_indicator"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
        .reset_index()
    )

    # Calculate cumulative probabilities
    cumulative_df = proportions_df[["semester_number"]].copy()
    active_population = 1.0  # Start with 100% of the population active
    cumulative_outcomes = {1: [], 2: [], 3: [], 4: []}

    for idx, row in proportions_df.iterrows():
        # Update cumulative probabilities based on remaining active population
        for col in [1, 4, 2, 3]:
            current_prob = row.get(col, 0) * active_population
            if idx == 0:
                cumulative_outcomes[col].append(current_prob)
            else:
                cumulative_outcomes[col].append(
                    cumulative_outcomes[col][-1] + current_prob
                )
        # Update active population based on -1 (active) + 4 (changed major)
        active_population *= (row.get(-1,0) + row.get(4,0)) # avoids errors that occur when no one is in category -1 or 4

    # Calculate -1 as the remaining active population
    cumulative_outcomes[-1] = [
        1.0 - (cumulative_outcomes[1][i] + cumulative_outcomes[2][i] + cumulative_outcomes[3][i])
        for i in range(len(proportions_df))
    ]

    for col in cumulative_outcomes:
        cumulative_df[col] = cumulative_outcomes[col]

    active_student_counts = input_df.groupby(['semester_number'])['student_ID'].count()

    return {
        "proportions_df": proportions_df,
        "cumulative_df": cumulative_df,
        "active_student_counts": active_student_counts
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
