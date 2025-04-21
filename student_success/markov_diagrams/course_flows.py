import pandas as pd


def analyze_course(course_name, df, major_matriculation, prerequisite_course=False, node_pie=False):
    """
    Analyze student performance and attempt statistics for a given course.

    Parameters
    ----------
    course_name : str
        Name of the course to analyze (e.g., 'Principles of Chemistry I')
    df : pandas.DataFrame
        Input DataFrame containing course data.
    major_matriculation : str
        Major for which the analysis is conducted. (e.g., 'CHM')
    prerequisite_course : str, optional
        Indicator for whether the course is a prerequisite (default is False).
    node_pie : bool, optional
        Indicator for whether to include pie charts for key demographics (default is False).

    Returns
    -------
    dict or None
        A dictionary containing the following descriptive statistics if course attempts exist:
            - 'first_pass_number': Number of students passing the course on the first attempt.
            - 'first_pass_proportion': Proportion of students passing the course on the first attempt.
            - 'first_DFW_number': Number of students receiving a D, F, or W grade on the first attempt.
            - 'first_DFW_proportion': Proportion of students receiving a D, F, or W grade on the first attempt.
            - 'proportion_DFW_repeat': Proportion of students repeating the course after initial failure.
            - 'second_attempt_number': Total number of second attempts for the course.
            - 'second_pass_number': Number of students passing the course on the second attempt.
            - 'second_pass_proportion': Proportion of students passing the course on the second attempt.
            - 'second_DFW_number': Number of students receiving a D, F, or W grade on the second attempt.
            - 'second_DFW_proportion': Proportion of students receiving a D, F, or W grade on the second attempt.
        Returns None if no attempts are found for the specified course.
    """

    if df.empty:
        print("DataFrame is empty.")
        return None

    course_df_all_attempts = df[df['course_title'] == course_name]
    course_df_all_attempts = course_df_all_attempts.sort_values(by=['student_ID', 'course_term'])
    print(f"Total attempts for {course_name}: {len(course_df_all_attempts)}")

    if course_df_all_attempts.empty:
        print(f"No attempts found for {course_name}.")
        return None

    course_df_first_attempts_all = course_df_all_attempts.drop_duplicates(subset=['student_ID'], keep='first')
    print(f"Number of unique students in first attempt of {course_name}: {len(course_df_first_attempts_all)}")

    desired_major_students = course_df_first_attempts_all[
        course_df_first_attempts_all['major_matriculation'] == major_matriculation
    ]['student_ID'].unique()
    print(f"Number of unique {major_matriculation} majors  : {len(desired_major_students)}")

    course_df = course_df_all_attempts[course_df_all_attempts['student_ID'].isin(desired_major_students)]
    course_df_first_attempts = course_df.drop_duplicates(subset=['student_ID'], keep='first')

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

    course_df_second_attempts = course_df_repeat_attempts_all[course_df_repeat_attempts_all.duplicated(subset=['student_ID'], keep='first')]

    print("Current course is:", course_name)

    grouped_second_attempters_df = course_df_all_attempts[
        course_df_all_attempts['major_matriculation'] == major_matriculation
    ].groupby('student_ID').filter(lambda x: len(x) > 1)

    first_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(0)
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

    descriptives = {
        "first_pass_number": first_pass_number,
        "first_pass_proportion": first_pass_proportion,
        "first_DFW_number": first_DFW_number,
        "first_DFW_proportion": first_DFW_proportion,
        "proportion_DFW_repeat": proportion_DFW_repeat,
        "second_attempt_number": second_attempt_number,
        "second_pass_number": second_pass_number,
        "second_pass_proportion": second_pass_proportion,
        "second_DFW_number": second_DFW_number,
        "second_DFW_proportion": second_DFW_proportion
    }

    return descriptives


def calculate_progression_to_next_course(current_course, next_course, df, major_matriculation):
    """
    Calculate the progression of students from a current course to a next course.

    Parameters
    ----------
    current_course : str
        The name of the current course.
    next_course : str
        The name of the next course.
    df : pandas DataFrame
        The DataFrame containing student enrollment data.
    major_matriculation : str
        The major matriculation of the students being considered.

    Returns
    -------
    tuple
        A tuple containing the proportion and number of students who passed the current course but did not take the next course,
        the proportion and number of students who passed the current course and took the next course, and a list of Student_IDs
        who took the next course.
    """
    df = df[df['major_matriculation'] == major_matriculation]

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


def calculate_alternate_entry(current_course, prior_course, df, major_matriculation):
    """
    Identify students who entered a course without passing the expected prerequisite.

    Parameters
    ----------
    current_course : str
        The course students enter (e.g., 'PRINCIPLES OF CHEMISTRY II').
    prior_course : str
        The expected prerequisite course (e.g., 'PRINCIPLES OF CHEMISTRY I').
    df : pd.DataFrame
        DataFrame containing student course history.
    major_matriculation : str
        The major matriculation filter to apply.

    Returns
    -------
    dict
        {
            'n_total': total number of students in current_course,
            'n_without_prior_pass': count who did not pass prior_course before taking current_course,
            'pct_alternate_entry': percent of students in current_course who did not pass prior_course
        }
    """
    df = df[df['major_matriculation'] == major_matriculation]

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
