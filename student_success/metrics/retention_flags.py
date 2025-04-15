import pandas as pd
import matplotlib as plt
import numpy as np
from student_success.utils.constants import STEM_CORE_MAJORS

# TODO: reduce redundancy with hazard_analysis functions and refactor accordingly

def generate_STEM_major_retention_flag(input_df, major_list=[], stem=True, major_col='major_term'):
    """
    Add retention flags for students whose earliest declared major is in a target list.

    This function creates a retention indicator for students who are still in their original
    major (defined by 'major_term_earliest') and, optionally, an additional indicator for
    whether their current major is part of a predefined set of STEM majors.

    Parameters
    ----------
    input_df : pd.DataFrame
        The input DataFrame containing at least the columns 'major_term', 'major_term_earliest', and optionally others.
    major_list : list, optional
        A list of major codes to identify the cohort of interest based on earliest declared major.
    stem : bool, optional
        Whether to add a flag for current enrollment in a core STEM major. Defaults to True.
    major_col : str, optional
        Column name used to represent the student's current major. Default is 'major_term'.

    Returns
    -------
    pd.DataFrame
        The input DataFrame (filtered to relevant students) with two new columns:
        - 'flag_retention_major': 1 if the current major matches the earliest declared major, 0 otherwise.
        - 'flag_retention_STEM': 1 if the current major is in MAJORS_STEM_CORE, 0 otherwise (only added if stem=True).

    Notes
    -----
    This function assumes that STEM_CORE_MAJORS is imported from `student_success.utils.constants`.
    """

    # Create a dataframe of all students for whom their earliest declared major was in the focal set of courses
    input_df = input_df[input_df['major_term_earliest'].isin(major_list)].copy()
    input_df.loc[:, 'flag_retention_major'] = (input_df[major_col] == input_df['major_term_earliest']).astype(int)

    # Add a flag for retention in STEM
    if stem:
        input_df['flag_retention_STEM'] = input_df[major_col].isin(STEM_CORE_MAJORS).astype(int)

    return input_df


def plot_retention_rate(cleaned_df, semester_col='semester_number', major_retention_col='flag_retention_major', stem_retention_col='flag_retention_STEM', stem_plot=True, major_plot=True, major_list=[], xlim_range = None):
    """
    Plots the retention rate for a specified major and optionally for STEM majors within a DataFrame.

    Parameters:
    - cleaned_df (pd.DataFrame): DataFrame containing student data.
    - semester_col (str): Column name for semester numbers.
    - major_retention_col (str): Column name indicating retention in the specified major.
    - stem_retention_col (str): Column name indicating retention in STEM majors.
    - stem_plot (bool): Flag to determine whether to plot STEM major retention rates. Defaults to True.
    - major_plot (bool): Flag to determine whether to plot specific major retention rates. Defaults to True.
    - major_list (list): list of string major codes that will be included in plot
    - xlim_range (tuple): A tuple specifying the (min, max) range for the x-axis. Default is None for auto-scaling.
    Returns:
    - None: Displays a plot of the retention rate alongside a histogram of total students per semester.

    Notes:
    - The function allows for separate or simultaneous plotting of retention rates for a specific major and STEM majors.
    - Retention rates are calculated as the mean percentage of students retained, with error bars representing the standard error of the mean.

    Example usage:
    - plot_retention_rate(cleaned_df, major='BIO')
    """
    #if major != 'All':
    major_df = cleaned_df[cleaned_df['major_earliest_term'].isin(major_list)].copy()
    #else:
    #    major_df = cleaned_df.copy()

    if major_plot:
        major_retention_stats = major_df.groupby(semester_col)[major_retention_col].agg(['mean', 'std', 'count']).reset_index()
        major_retention_stats['mean'] *= 100
        major_retention_stats['std'] = (major_retention_stats['std'] / np.sqrt(major_retention_stats['count'])) * 100

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.errorbar(major_retention_stats[semester_col], major_retention_stats['mean'], yerr=major_retention_stats['std'], fmt='o-', capsize=5, label='Major Retention Rate')
        ax1.set_title(f'Cumulative {major_list} Major Retention Rate')
        ax1.set_xlabel('Semester Number')
        ax1.set_ylabel('Retention Rate (%)', color='tab:blue')
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.bar(major_retention_stats[semester_col], major_retention_stats['count'], alpha=0.3, color='grey', label='Total Students')
        ax2.set_ylabel('Number of Students', color='grey')
        ax2.tick_params(axis='y', labelcolor='grey')

        # Set x-axis limit if provided
        if xlim_range:
            ax1.set_xlim(xlim_range)
            ax2.set_xlim(xlim_range)

        fig.tight_layout()
        fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
        plt.show()

    if stem_plot:
        stem_retention_stats = major_df.groupby(semester_col)[stem_retention_col].agg(['mean', 'std', 'count']).reset_index()
        stem_retention_stats['mean'] *= 100
        stem_retention_stats['std'] = (stem_retention_stats['std'] / np.sqrt(stem_retention_stats['count'])) * 100

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.errorbar(stem_retention_stats[semester_col], stem_retention_stats['mean'], yerr=stem_retention_stats['std'], fmt='o-', capsize=5, label='STEM Retention Rate')
        ax1.set_title('Cumulative STEM Major Retention Rate')
        ax1.set_xlabel('Semester Number')
        ax1.set_ylabel('Retention Rate (%)', color='tab:blue')
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.bar(stem_retention_stats[semester_col], stem_retention_stats['count'], alpha=0.3, color='grey', label='Total Students')
        ax2.set_ylabel('Number of Students', color='grey')
        ax2.tick_params(axis='y', labelcolor='grey')

        # Set x-axis limit if provided
        if xlim_range:
            ax1.set_xlim(xlim_range)
            ax2.set_xlim(xlim_range)

        fig.tight_layout()
        fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
        plt.show()


def plot_cumulative_retention_rate(cleaned_df, semester_col='semester_number', major_retention_col='flag_retention_major',
                                   stem_retention_col='flag_retention_STEM', grad_col='graduation_flag',
                                   stem_plot=True, major_plot=True, major_list=[]):
    """
    Plots cumulative retention rates for specific subpopulations (major retention, university retention, and graduation).

    Parameters:
    - cleaned_df (pd.DataFrame): DataFrame containing student data.
    - semester_col (str): Column name for semester numbers.
    - major_retention_col (str): Column name indicating retention in the specified major.
    - stem_retention_col (str): Column name indicating retention in STEM majors.
    - grad_col (str): Column name indicating if the student has graduated.
    - stem_plot (bool): Flag to determine whether to plot STEM major retention rates. Defaults to True.
    - major_plot (bool): Flag to determine whether to plot specific major retention rates. Defaults to True.
    - major_list (list): list of string major codes that will be included in the plot.

    Returns:
    - None: Displays a plot of the cumulative retention rates.
    """

    major_df = cleaned_df[cleaned_df['major_earliest_term'].isin(major_list)].copy()

    if major_plot:
        # Calculate cumulative retention, graduation, and dropout rates
        major_retention_stats = major_df.groupby(semester_col)[major_retention_col].mean().cumsum().reset_index()
        major_retention_stats['cumulative_graduation'] = major_df.groupby(semester_col)[grad_col].mean().cumsum().reset_index(drop=True)
        major_retention_stats['cumulative_leaving_university'] = 1 - (major_retention_stats[major_retention_col] + major_retention_stats['cumulative_graduation'])

        # Plot
        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.plot(major_retention_stats[semester_col], major_retention_stats[major_retention_col] * 100, 'b-', label='Major Retention Rate')
        ax1.plot(major_retention_stats[semester_col], major_retention_stats['cumulative_graduation'] * 100, 'g-', label='Graduation Rate')
        ax1.plot(major_retention_stats[semester_col], major_retention_stats['cumulative_leaving_university'] * 100, 'r-', label='University Leaving Rate')

        ax1.set_title(f'Cumulative {major_list} Major Retention, Graduation, and Leaving Rates')
        ax1.set_xlabel('Semester Number')
        ax1.set_ylabel('Rate (%)')
        ax1.grid(True)
        ax1.legend(loc='upper right')

        plt.tight_layout()
        plt.show()


def plot_major_retention_rate(cleaned_df, major='All', student_id_col='student_ID', major_col='major_matriculation',
                              flag_col='flag_major_retention', semester_col='semester_number'):
    """
    Calculates and plots the retention rate for a specified major across semesters along with a histogram showing
    the total number of students per semester.

    Parameters:
    - cleaned_df (pd.DataFrame): DataFrame with student data.
    - major (str): Specific major to analyze. Default 'All' analyzes all majors.
    - student_id_col (str): Column name for student IDs.
    - major_col (str): Column name for students' majors.
    - flag_col (str): Column name indicating retention in the major.
    - semester_col (str): Column name for semester number.

    Returns:
    - None: Displays a plot of the retention rate alongside a histogram of total students per semester.

    Notes:
    - Created out of code developed by Paul Ulrich (2024-06-18) using ChatGPT 4.
    """
    if major != 'All':
        major_df = cleaned_df[cleaned_df[major_col] == major].copy()
    else:
        major_df = cleaned_df.copy()

    print(f'Unique students in {major}:', len(major_df[student_id_col].unique()), '(Number of records: ', len(major_df), ')')

    def calculate_retention(group):
        retained = group[flag_col].sum()
        total_students = len(group)
        retention = retained / total_students  # as a proportion
        std_dev = np.sqrt(retention * (1 - retention) / total_students) * 100  # Convert the result to percentage
        return pd.Series({'retention': retention * 100, 'std_dev': std_dev, 'total_students': total_students})

    retention_stats = major_df.groupby(semester_col).apply(calculate_retention).reset_index()

    # Plotting with error bars and a secondary axis for total students
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.errorbar(retention_stats[semester_col], retention_stats['retention'], yerr=retention_stats['std_dev'], fmt='o-', capsize=5, label='Retention Rate')
    ax1.set_title(f'Cumulative {major} Major Retention Rate')
    ax1.set_xlabel('Semester Number')
    ax1.set_ylabel('Cumulative Retention Rate (%)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.bar(retention_stats[semester_col], retention_stats['total_students'], alpha=0.3, color='grey', label='Total Students')
    ax2.set_ylabel('Number of Students', color='grey')
    ax2.tick_params(axis='y', labelcolor='grey')

    fig.tight_layout()
    fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.show()

# Example of how to use the function:
# plot_major_retention_rate(cleaned_df, major='BIO')
def major_retention(demographics_df, years, major_code, student_ids):
    """
    Calculate and analyze the retention and graduation metrics for students within a specific major over multiple academic years.

    This function assesses student retention by calculating the running sum of academic years in which students were retained in a specified major. It also analyzes major change behavior and graduation rates.

    Parameters:
    ----------
    demographics_df : DataFrame
        A pandas DataFrame containing demographic and academic data for students.
    years : list
        List of academic years to analyze.
    major_code : int or str
        The major code to analyze retention for.
    student_ids : list
        List of student IDs to include in the analysis. This can be all students or a filtered group, such as first-time, full-year students.

    Returns:
    -------
    tuple
        Returns two pandas DataFrames:
        - major_retention_df: DataFrame containing detailed retention data for each student per semester.
        - major_count_df: DataFrame summarizing the count and percentage of students who graduated in each major, including statistics on semesters before major change and till graduation.

    Notes:
    -----
    - The analysis excludes students who earn two degrees to simplify the analysis. This exclusion is noted on 2023-08-14.
    - Student IDs can be generated via list(df['Student_ID'].unique()) or using student_success.utilityfunctions.ftfy(df) for 'ftfy' students.

    Examples:
    --------
    >>> demographics_df = pd.DataFrame({...})
    >>> years = [2021, 2022]
    >>> major_code = 101
    >>> student_ids = [12345, 67890]
    >>> major_retention_df, major_count_df = major_retention(demographics_df, years, major_code, student_ids)
    """

    #running sum of the number of academic years in which a student has been retained in the major
    def calculate_running_retention_flag(group):
        """
        Calculates a running sum of the number of academic years in which a student has been retained in their major.

        This function iterates over each row of a grouped DataFrame (grouped by student), and tracks the count of academic
        years a student is retained in the same major. It updates the DataFrame with a new column 'major_retention_flag_running'
        that contains the running total of retention years.

        Parameters:
        ----------
        group : DataFrame
            A pandas DataFrame grouped by student, typically containing columns for academic years and retention flags.

        Returns:
        -------
        DataFrame
            The input DataFrame with an additional column 'major_retention_flag_running' which holds the running count of retention
            years for each student.

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
        last_year = None #stores the academic year iterator for the loop
        running_flags = []

        for _, row in group.iterrows():
            if row['major_retention_flag'] == 1 and row['AcademicYear'] != last_year:
                running_count += 1

            running_flags.append(running_count)
            last_year = row['AcademicYear']

        group['major_retention_flag_running'] = running_flags
        return group

    records = [] #a temporary variable to which data will be added; this will ultimately be returned as a dataframe

    # print(len(demographics_df))
    # Filter demographics_df for the students we care about
    working_df = demographics_df[demographics_df['student_ID'].isin(student_ids)]

    # NOTE (2023-08-14) this analysis excludes those who earn two BS to keep things simple; not sure this is the best approach
    mask = working_df.duplicated(subset=['student_ID', 'demographics_term'], keep=False)  # Create a mask for duplicate rows where a student earns two degrees
    working_df = working_df[~mask]  # Apply the mask to keep only non-duplicate rows; that is, exclude those students who earned two BS
    #print(len(working_df))

    #loop through years and semesters to generate flags
    for academicyear in years:
        semesters = utilityfunctions.create_semesters([academicyear])

        # Filter to semesters associated with argument years
        df_filtered = working_df[working_df['demographics_term'].isin(semesters)]
        #print(len(df_filtered))
        for student in student_ids:
            student_df = df_filtered[df_filtered['student_ID'] == student]

            for semester in semesters:
                semester_df = student_df[student_df['demographics_term'] == semester]

                if semester_df.empty:
                    continue

                #Flag non-graduated students as 0 and graduated students as 1
                #TO DO: Find a way for grad_flag to be set to 1 for the last semester of the degree rather than fixed characteristic
                if (semester_df[((semester_df['student_ID'] == student) & (semester_df['Grad_term'] > 0))].empty):
                    grad_flag = 0
                else:
                    grad_flag = 1

                #indicate if student is still in the indicated major for this semester
                major_retention_flag = int((semester_df['major_term'] == major_code).all())
                major = semester_df['major_term'].item()
                grad_term = semester_df['Grad_term'].item()

                #add the semester and data for current student to the records list
                records.append({
                    'student_ID': student,
                    'semester': semester,
                    'AcademicYear': academicyear,
                    'major': major,
                    'major_retention_flag': major_retention_flag,
                    'grad_flag': grad_flag,
                    'grad_term': grad_term
                })

    #convert records to a single dataframe
    major_retention_df = pd.DataFrame(records)

    #for semesters of each academic year, calculate a running sum of how many semesters they were retained in major_code
    major_retention_df= major_retention_df.groupby('student_ID').apply(calculate_running_retention_flag).reset_index(drop=True)

    #for students who changed major, it is helpful to know when they did this to determine where the curriculum structure could be affecting their decisions
    major_changed_df = major_retention_df[major_retention_df['major'] != major_code]  # create dataframe comprised of all students who changed to a different major
    major_changed_df = major_changed_df.reset_index(drop=True)  # reset index to ensure it is contiguous
    major_changed_df = major_changed_df.sort_values(by=['semester'], ascending=True)
    idx = major_changed_df.groupby('student_ID')['semester'].idxmin()  # Find index of row with smallest 'Semester' for each 'Student_ID'
    major_changed_df = major_changed_df.loc[idx]
    major_changed_df.rename(columns={'semester': 'major_change_semester'},inplace=True)  # rename the column to avoid confusion
    major_retention_df = pd.merge(major_retention_df, major_changed_df[['student_ID', 'major_change_semester']], on='student_ID', how = 'left', validate = 'many_to_one')

    # Determine how many semesters passed before student changed major
    # Group by 'Student_ID' and 'major_change_semester', then apply a lambda function to calculate the count
    semesters_before_major_change_df = (
        major_retention_df.groupby(['student_ID', 'major_change_semester'])
        .apply(lambda x: (x['semester'] < x['major_change_semester']).sum())
        .reset_index(name='semesters_before_major_change')
    )
    major_retention_df = pd.merge(major_retention_df, semesters_before_major_change_df, on=['student_ID', 'major_change_semester'], how ='left')
    # major_retention_df['total_semesters'] = major_retention_df.groupby('Student_ID').size()
    major_retention_df['total_semesters'] = major_retention_df.groupby('student_ID')['student_ID'].transform('size')

    # Create a dataframe reportingt those who graduated that includes the last semester of their BS coursework
    grad_df = major_retention_df[(major_retention_df['grad_flag'] == 1)]  # creates a dataframe comprised of all students who graduated
    grad_df = grad_df.reset_index(drop=True)  # reset the index to ensure it is contiguous
    # grad_df['semesters_till_graduation'] = grad_df.groupby('Student_ID').size()
    idx_last_semester = grad_df.groupby('student_ID')['semester'].idxmax()  # Find the index of the row with the largest 'Semester' for each 'Student_ID'

    #idx_first_semester = grad_df.groupby('Student_ID')['Semester'].idxmin()
    #grad_df_last_semester = grad_df.loc[idx_last_semester]  # filter grad_df by the index of the row for the LAST semester in BS
    #grad_df_first_semester = grad_df.loc[idx_first_semester] # filter grad_df by the index of the row for the FIRST semester

    grad_df = grad_df.loc[idx_last_semester]

    #generate a summary table that reports the majors graduated with
    major_count_df = grad_df.groupby(['major'])['major'].count().reset_index(name='count')
    major_count_df = major_count_df.sort_values(by=['count'], ascending=False)
    major_count_df['percentage'] = 100 * major_count_df['count'] / sum(major_count_df['count'])
    major_count_df['count'].sum()
    majors_list = list(major_count_df['major'])
    major_change_time_means = []
    for major in majors_list:
        mean_semesters_major_change = grad_df[grad_df['major'] == major]['semesters_before_major_change'].mean()
        std_semesters_major_change = grad_df[grad_df['major'] == major]['semesters_before_major_change'].std()
        mean_semesters_graduation = grad_df[grad_df['major'] == major]['total_semesters'].mean()
        std_semesters_graduation = grad_df[grad_df['major'] == major]['total_semesters'].std()
        #print(major, num_semesters_graduation)
        #A small group of students will switch to a different major and back during their education.
        #In this case, when major_code = major gradauted with, the code will calculate the mean # of semesters before change.
        #For clarity, I added a conditional block that reports how many students are doing this.
        if major == major_code:
            count = grad_df[(grad_df['major'] == major) & (grad_df['semesters_before_major_change'].notna())].count()
            mean_semesters_major_change = str(mean_semesters_major_change) + " (" + str(count['major']) + " students)"

        major_change_time_means.append({
            'major': major,
            'mean # of semesters before change': mean_semesters_major_change,
            'S.D. of semesters before change': std_semesters_major_change,
            'mean # of semesters till graduation': mean_semesters_graduation,
            'S.D. of semesters till graduation' : std_semesters_graduation
        })
    major_count_df = pd.merge(major_count_df, pd.DataFrame(major_change_time_means), on = 'major', how = 'left', validate = 'one_to_one')

    return major_retention_df, major_count_df
