"""
Analysis utilities for course progression, repeat patterns, and prerequisite pathways.

This module provides functions to quantify how students flow through key gateway courses,
including repeat attempts, success/failure rates, progression to sequenced courses, and
alternate entry points. Designed for use in building course-flow visualizations and
informing curriculum analysis.

Functions
---------
- ``analyze_course`` :
    Summarize first/second attempt outcomes, repeat rates, and (optionally) demographic
    breakdowns for a single course.
- ``calculate_progression_to_next_course`` :
    Evaluate how many students who passed a given course progressed into the next
    course in a sequence.
- ``calculate_alternate_entry`` :
    Identify students entering a downstream course without having passed the expected
    prerequisite.

Notes
-----
- All functions expect a long-format DataFrame with at least:
  ``student_ID``, ``course_title``, ``course_term``, and ``course_grade_letter_simp``.
- Demographic breakdowns in ``analyze_course`` require a valid flag column and are mapped
  using ``DEMOGRAPHIC_COLOR_MAPS`` from ``student_success.utils.constants``.
- Grades are assumed to be simplified into {A, B, C, D, F, W} before analysis. Use
  ``utils.grade_utils.filter_valid_letter_grades()`` as a preprocessing step.
- Outputs are returned as dictionaries with counts, proportions, and ID lists to support
  both descriptive reporting and visualization layers.

TODO
----

- Externalize demographic proportion logic into ``utils.demographics_utils`` to avoid
  duplication.
- Expand progression logic to account for time-to-next-course (not just ever/never).
"""



import pandas as pd
from student_success.utils.constants import DEMOGRAPHIC_COLOR_MAPS


def analyze_course(course_name, df, major_matriculation_column='major_term_earliest', target_major_code=None, prerequisite_course=False, node_pie=False, demographics_flag_col=None):
    """
    Analyze student performance, repeat rates, and (optionally) demographic composition for a specific course.

    Parameters
    ----------
    course_name : str
        The course title to analyze (e.g., 'Principles of Chemistry I').
    df : pandas.DataFrame
        Input dataframe containing student course records.
    major_matriculation_column : str, optional
        Column indicating each student’s major at matriculation. Default is 'major_term_earliest'.
    target_major_code : str, optional
        If specified, restricts analysis to students with this major.
    prerequisite_course : bool, optional
        Whether the course is treated as a prerequisite (default is False).
    node_pie : bool, optional
        If True, compute demographic breakdowns for use in pie charts.
    demographics_flag_col : str, optional
        Name of binary demographic column used to generate pie charts (e.g., 'flag_sex').

    Returns
    -------
    dict or None
        A dictionary with course performance and (optional) demographic breakdowns:

            - 'first_pass_number': Count of students passing on first attempt.
            - 'first_pass_proportion': Proportion passing on first attempt.
            - 'first_DFW_number': Count receiving D, F, or W on first attempt.
            - 'first_DFW_proportion': Proportion with D, F, or W on first attempt.
            - 'proportion_DFW_repeat': Proportion of DFW students who repeated.
            - 'second_attempt_number': Count of second attempts.
            - 'second_pass_number': Count passing on second attempt.
            - 'second_pass_proportion': Proportion passing on second attempt.
            - 'second_DFW_number': Count with D/F/W on second attempt.
            - 'second_DFW_proportion': Proportion with D/F/W on second attempt.
            - 'first_attempt_demographic_proportions': Optional dict of {color: proportion} for pie node.
            - 'second_attempt_demographic_proportions': Optional dict of {color: proportion} for pie node.

        Returns None if the course is not found in the dataset.
    """

    if df.empty:
        print("DataFrame is empty.")
        return None

    print("Current course is:", course_name)
    course_df_all_attempts = df[df['course_title'] == course_name]
    course_df_all_attempts = course_df_all_attempts.sort_values(by=['student_ID', 'course_term'])
    print(f"Total attempts for {course_name}: {len(course_df_all_attempts)}")

    if course_df_all_attempts.empty:
        print(f"No attempts found for {course_name}.")
        return None

    course_df_first_attempts_all = course_df_all_attempts.drop_duplicates(subset=['student_ID'], keep='first')
    print(f"Number of unique students in first attempt of {course_name}: {len(course_df_first_attempts_all)}")

    if target_major_code:
        desired_major_students = course_df_first_attempts_all[
            course_df_first_attempts_all[major_matriculation_column] == target_major_code
            ]['student_ID'].unique()
        print(f"Number of unique {target_major_code} majors  : {len(desired_major_students)}")
        course_df = course_df_all_attempts[course_df_all_attempts['student_ID'].isin(desired_major_students)]
        course_df_first_attempts = course_df.drop_duplicates(subset=['student_ID'], keep='first')
    else:
        course_df = course_df_all_attempts
        course_df_first_attempts = course_df.drop_duplicates(subset=['student_ID'], keep='first')
        print(f"Number of unique students (no major filtering)  : {len(course_df_first_attempts_all['student_ID'].unique())}")

    print(course_df_first_attempts['course_grade_letter_simp'].unique())
    first_pass_number = len(course_df_first_attempts[course_df_first_attempts['course_grade_letter_simp'].isin(['A', 'B', 'C'])])
    print(f"First pass number : {first_pass_number}")

    first_pass_proportion = first_pass_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0
    first_DFW_number = len(course_df_first_attempts[course_df_first_attempts['course_grade_letter_simp'].isin(['D', 'F', 'W'])])
    print(f"First DFW number : {first_DFW_number}")

    first_DFW_proportion = first_DFW_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0

    course_df_repeat_attempts_all = course_df[course_df.duplicated(subset=['student_ID'], keep=False)]
    print("Number of all repeats who did not pass the first time :", len(course_df_repeat_attempts_all))
    print("Number of all unique students who did not pass the first time :", len(course_df_repeat_attempts_all['student_ID'].unique()))

    if target_major_code:
        grouped_second_attempters_df = course_df_all_attempts[
            course_df_all_attempts[major_matriculation_column] == target_major_code
        ].groupby('student_ID').filter(lambda x: len(x) > 1)
    else:
        grouped_second_attempters_df = course_df_all_attempts.groupby('student_ID').filter(lambda x: len(x) > 1)

    second_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(1)

    print("Length of first attempt majors:", len(course_df_first_attempts['student_ID'].unique()))

    proportion_DFW_repeat = len(second_attempt_df) / first_DFW_number if first_DFW_number > 0 else 0
    print("Proportion DFW repeat:", proportion_DFW_repeat)

    second_attempt_number = len(second_attempt_df)
    print("Second attempt number:", second_attempt_number)

    second_pass_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['A', 'B', 'C'])]['student_ID'].nunique()
    print(f"Number of students who passed the second attempt of {course_name}: {second_pass_number}")

    second_pass_proportion = second_pass_number / len(grouped_second_attempters_df['student_ID'].unique()) if len(grouped_second_attempters_df) > 0 else 0

    second_DFW_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])]['student_ID'].nunique()
    second_DFW_proportion = second_DFW_number / len(grouped_second_attempters_df['student_ID'].unique()) if len(grouped_second_attempters_df) > 0 else 0

    print(f"Number of students who failed the second attempt of {course_name}: {second_DFW_number}")

    if node_pie and demographics_flag_col is not None:
        if demographics_flag_col not in DEMOGRAPHIC_COLOR_MAPS:
            raise ValueError(
                f"Demographic column '{demographics_flag_col}' is not recognized.\n"
                f"Valid options: {list(DEMOGRAPHIC_COLOR_MAPS.keys())}"
            )

        # TODO: Create a demographics helper function in utils.demographics_utils.py
        def compute_proportions(df, col, mapping = None):
            total = len(df)
            if total == 0:
                return {}
            proportions = df[col].value_counts(normalize = True).to_dict()
            if mapping:
                # Recolor using map and remove missing values
                return {mapping[k]: v for k, v in proportions.items() if k in mapping}
            return proportions

        color_map = DEMOGRAPHIC_COLOR_MAPS.get(demographics_flag_col)
        first_attempt_demographic_proportions = compute_proportions(df = course_df_first_attempts, col = demographics_flag_col,
                                                        mapping=color_map)
        first_attempt_DFW_demographic_proportions = compute_proportions(
            df=course_df_first_attempts[course_df_first_attempts['course_grade_letter_simp'].isin(['D', 'F', 'W'])],
            col=demographics_flag_col,
            mapping=color_map
        )

        second_attempt_demographic_proportions = compute_proportions(df=second_attempt_df, col=demographics_flag_col,
                                                                     mapping=color_map)
        second_attempt_DFW_demographic_proportions = compute_proportions(
            df=second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])],
            col=demographics_flag_col,
            mapping=color_map
        )

        print(f"analyze_course() 1st attempt demographic proportions for {course_name}: {first_attempt_demographic_proportions}")
        print(f"analyze_course() 2nd attempt demographic proportions for {course_name}: {second_attempt_demographic_proportions}")

    descriptives = {
        "first_attempt_demographic_proportions": first_attempt_demographic_proportions,
        "first_pass_number": first_pass_number,
        "first_pass_proportion": first_pass_proportion,
        "first_DFW_number": first_DFW_number,
        "first_DFW_proportion": first_DFW_proportion,
        "first_DFW_demographic_proportions": first_attempt_DFW_demographic_proportions,
        "proportion_DFW_repeat": proportion_DFW_repeat,
        "second_attempt_demographic_proportions": second_attempt_demographic_proportions,
        "second_attempt_number": second_attempt_number,
        "second_pass_number": second_pass_number,
        "second_pass_proportion": second_pass_proportion,
        "second_DFW_number": second_DFW_number,
        "second_DFW_proportion": second_DFW_proportion,
        "second_DFW_demographic_proportions": second_attempt_DFW_demographic_proportions
    }

    return descriptives


def calculate_progression_to_next_course(current_course, next_course, df, target_major_code=None, major_matriculation_column='major_term_earliest'):
    """
    Calculate how many students progressed from one course to the next after passing.

    Parameters
    ----------
    current_course : str
        Course the student completed first (e.g., 'CHEM 1211K').
    next_course : str
        Course that follows in the sequence (e.g., 'CHEM 1212K').
    df : pandas.DataFrame
        DataFrame with student course records.
    target_major_code : str, optional
        If provided, restricts analysis to students with this major at matriculation.
    major_matriculation_column : str, optional
        Name of column identifying the student’s entry major (default is 'major_term_earliest').

    Returns
    -------
    dict
        Dictionary containing:
            - 'proportion_not_taking_next': % of passed students who did not take the next course.
            - 'number_not_taking_next': Raw count of these students.
            - 'proportion_taking_next': % of passed students who continued.
            - 'number_taking_next': Raw count of these students.
            - 'students_who_did_take_next': List of student_IDs who progressed.
    """

    if target_major_code:
        df = df[df[major_matriculation_column] == target_major_code]

    # Step 1: Get second attempt performance in current course
    filtered_df = df[df['course_title'] == current_course]
    grouped_second_attempters_df = filtered_df.groupby('student_ID').filter(lambda x: len(x) > 1)
    second_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(1)

    second_attempt_pass_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['A', 'B', 'C'])]['student_ID'].nunique()
    second_attempt_DFW_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])]['student_ID'].nunique()

    # Step 2: Get all students who passed the course
    passed_students = df[
        (df['course_title'] == current_course) &
        (df['course_grade_letter_simp'].isin(['A', 'B', 'C']))
    ]['student_ID'].unique()

    # Step 3: Partition those who did/didn't take next course
    did_not_take_next = [
        student for student in passed_students
        if student not in df[df['course_title'] == next_course]['student_ID'].unique()
    ]
    did_take_next = [
        student for student in passed_students
        if student in df[df['course_title'] == next_course]['student_ID'].unique()
    ]

    exploratory_df = df[(df['student_ID'].isin(did_take_next)) & (df['course_title'] == current_course)]
    second_attempts_dfw = exploratory_df.groupby('student_ID').filter(
        lambda x: len(x) == 2 and not any(x['course_grade_letter_simp'].isin(['A', 'B', 'C']))
    )

    # Step 4: Calculate metrics
    proportion_not_taking_next = len(did_not_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_not_taking_next = len(did_not_take_next)
    proportion_taking_next = len(did_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_taking_next = len(did_take_next)

    print(f"Number of students who passed {current_course} but did not take {next_course} : ", number_not_taking_next)

    return {
        'proportion_not_taking_next': proportion_not_taking_next,
        'number_not_taking_next': number_not_taking_next,
        'proportion_taking_next': proportion_taking_next,
        'number_taking_next': number_taking_next,
        'students_who_did_take_next': did_take_next
    }


def calculate_alternate_entry(current_course, prior_course, df, target_major_code=None, major_matriculation_column='major_term_earliest'):
    """
    Identify students who enrolled in a course without passing the expected prerequisite.

    Parameters
    ----------
    current_course : str
        The downstream course (e.g., 'CHEM 1212K').
    prior_course : str
        The expected prerequisite course (e.g., 'CHEM 1211K').
    df : pandas.DataFrame
        DataFrame containing student course history. Must include 'student_ID', 'course_title',
        'course_grade_letter_simp', and the specified major column.
    target_major_code : str, optional
        If provided, limits analysis to students with this major at matriculation.
    major_matriculation_column : str, optional
        Column name for student’s matriculation major (default is 'major_term_earliest').

    Returns
    -------
    dict
        A dictionary summarizing alternate entries:
            - 'n_total': Total number of students in the current course.
            - 'n_without_prior_pass': Count of students who skipped or failed the prerequisite.
            - 'pct_alternate_entry': % of students without prior course pass.
            - 'alt_entry_ids': List of student_IDs who did not pass the prerequisite.
    """

    if target_major_code:
        df = df[df[major_matriculation_column] == target_major_code]

    passed_prior = df[
        (df['course_title'] == prior_course) &
        (df['course_grade_letter_simp'].isin(['A', 'B', 'C']))
    ]['student_ID'].unique()

    took_current = df[df['course_title'] == current_course]['student_ID'].unique()

    alt_entry_ids = [sid for sid in took_current if sid not in passed_prior]

    print(f"Number of students in {current_course} who did not pass {prior_course}: {len(alt_entry_ids)}")

    return {
        'n_total': len(took_current),
        'n_without_prior_pass': len(alt_entry_ids),
        'pct_alternate_entry': len(alt_entry_ids) / len(took_current) * 100 if len(took_current) > 0 else 0,
        'alt_entry_ids': alt_entry_ids
    }
