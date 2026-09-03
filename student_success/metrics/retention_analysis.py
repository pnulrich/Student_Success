import pandas as pd
from student_success.utils.time_utils import create_semesters


def calculate_running_retention_flag(group: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a running sum of the number of academic years in which a student has been retained in their major.

    This function iterates over each row of a grouped DataFrame (grouped by student), and tracks the count of academic
    years a student is retained in the same major. It updates the DataFrame with a new column 'major_retention_flag_running'
    that contains the running total of retention years.

    Parameters
    ----------
    group : pd.DataFrame
        Grouped DataFrame for a single student.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with an added column 'major_retention_flag_running'.

            Example:
    --------
    >>> data = pd.DataFrame({
            'student_ID': [1, 1, 1, 2, 2],
            'AcademicYear': [2018, 2019, 2020, 2018, 2019],
            'major_retention_flag': [1, 1, 1, 1, 0]
        })
    >>> grouped_data = data.groupby('student_ID')
    >>> result = grouped_data.apply(calculate_running_retention_flag)
    >>> print(result)
       student_ID  AcademicYear  major_retention_flag  major_retention_flag_running
    0           1          2018                     1                            1
    1           1          2019                     1                            2
    2           1          2020                     1                            3
    3           2          2018                     1                            1
    4           2          2019                     0                            1
    """
    running_count = 0
    last_year = None # stores the academic year iterator for the loop
    running_flags = []

    for _, row in group.iterrows():
        if row['major_retention_flag'] == 1 and row['AcademicYear'] != last_year:
            running_count += 1
        running_flags.append(running_count)
        last_year = row['AcademicYear']

    group['major_retention_flag_running'] = running_flags
    return group

def major_retention(demographics_df, years, major_code, student_ids):
    """
    Analyze retention and graduation for a major over time.

    Parameters
    ----------
    demographics_df : pd.DataFrame
    years : list[int]
    major_code : str or int
    student_ids : list[int]

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - major_retention_df: longitudinal data by student-semester
        - major_count_df: graduation summary with change timing
    """

    # === Step 1: Filter and clean dataset ===
    working_df = demographics_df[demographics_df['student_ID'].isin(student_ids)]

    # Remove students with multiple degrees in the same semester
    mask = working_df.duplicated(subset=['student_ID', 'demographics_term'], keep=False)
    working_df = working_df[~mask]

    records = []

    # === Step 2: Generate longitudinal records ===
    for academicyear in years:
        semesters = create_semesters([academicyear])
        df_filtered = working_df[working_df['demographics_term'].isin(semesters)]

        for student in student_ids:
            student_df = df_filtered[df_filtered['student_ID'] == student]

            for semester in semesters:
                semester_df = student_df[student_df['demographics_term'] == semester]
                if semester_df.empty:
                    continue

                grad_flag = 0 if semester_df[(semester_df['Grad_term'] > 0)].empty else 1
                major_retention_flag = int((semester_df['major_term'] == major_code).all())

                records.append({
                    'student_ID': student,
                    'semester': semester,
                    'AcademicYear': academicyear,
                    'major': semester_df['major_term'].item(),
                    'major_retention_flag': major_retention_flag,
                    'grad_flag': grad_flag,
                    'grad_term': semester_df['Grad_term'].item()
                })

    major_retention_df = pd.DataFrame(records)

    # === Step 3: Calculate running retention flag ===
    major_retention_df = major_retention_df.groupby('student_ID').apply(calculate_running_retention_flag).reset_index(drop=True)

    # === Step 4: Identify semester when major was changed ===
    major_changed_df = major_retention_df[major_retention_df['major'] != major_code].copy()
    major_changed_df = major_changed_df.sort_values(by='semester')
    idx = major_changed_df.groupby('student_ID')['semester'].idxmin()
    major_changed_df = major_changed_df.loc[idx]
    major_changed_df.rename(columns={'semester': 'major_change_semester'}, inplace=True)

    # TODO: When upgrading pandas ≥ 2.x, revisit this groupby-apply to remove DeprecationWarning
    major_retention_df = pd.merge(
        major_retention_df,
        major_changed_df[['student_ID', 'major_change_semester']],
        on='student_ID',
        how='left',
        validate='many_to_one'
    )

    # === Step 5: Calculate semesters before major change ===
    # TODO: When upgrading pandas ≥ 2.x, revisit this groupby-apply to remove DeprecationWarning
    semesters_before_major_change_df = (
        major_retention_df.groupby(['student_ID', 'major_change_semester'])
        .apply(lambda x: (x['semester'] < x['major_change_semester']).sum())
        .reset_index(name='semesters_before_major_change')
    )
    major_retention_df = pd.merge(
        major_retention_df,
        semesters_before_major_change_df,
        on=['student_ID', 'major_change_semester'],
        how='left'
    )
    major_retention_df['total_semesters'] = major_retention_df.groupby('student_ID')['student_ID'].transform('size')

    # === Step 6: Graduation summary stats ===
    grad_df = major_retention_df[major_retention_df['grad_flag'] == 1].copy()
    idx_last_semester = grad_df.groupby('student_ID')['semester'].idxmax()
    grad_df = grad_df.loc[idx_last_semester]

    major_count_df = grad_df.groupby('major')['major'].count().reset_index(name='count')
    major_count_df = major_count_df.sort_values(by='count', ascending=False)
    major_count_df['percentage'] = 100 * major_count_df['count'] / major_count_df['count'].sum()

    major_change_time_means = []
    for major in major_count_df['major']:
        df = grad_df[grad_df['major'] == major]
        row = {
            'major': major,
            'mean # of semesters before change': df['semesters_before_major_change'].mean(),
            'S.D. of semesters before change': df['semesters_before_major_change'].std(),
            'mean # of semesters till graduation': df['total_semesters'].mean(),
            'S.D. of semesters till graduation': df['total_semesters'].std()
        }

        if major == major_code:
            count = df[df['semesters_before_major_change'].notna()].shape[0]
            row['mean # of semesters before change'] = f"{row['mean # of semesters before change']} ({count} students)"

        major_change_time_means.append(row)

    major_count_df = pd.merge(
        major_count_df,
        pd.DataFrame(major_change_time_means),
        on='major',
        how='left',
        validate='one_to_one'
    )

    return major_retention_df, major_count_df
