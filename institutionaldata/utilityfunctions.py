# Let's write a helper function to adjust the graduation term to the end of the term
import pandas as pd
from tkinter import filedialog as fd
import tkinter as tk
import re
import numpy as np

#[Utility function] permit simple ciphering of Student_ID numbers; depending on input, returns either a dataframe or a string
#working_df : dataframe where Student_ID is the column to be ciphered
#cipher : a string of characters length of Student_ID; DON'T FORGET THIS AND DO NOT POST PUBLICALLY
def scramble_ID(input_data, cipher):
    """
        Scramble student IDs based on a cipher.

        Parameters
        ----------
        input_data : pandas.DataFrame or str
            The input data to scramble. If a DataFrame is provided, it should contain a column named 'student_ID'
            with the original student IDs. If a string is provided, it represents a single student ID to be scrambled.
        cipher : str
            The cipher used for scrambling. It should be a string of exactly 10 characters representing the mapping
            of each digit (0-9) to a new character.

        Returns
        -------
        pandas.DataFrame or str or None
            - If input_data is a DataFrame, returns a copy of the DataFrame with the 'student_ID' column scrambled
              according to the provided cipher.
            - If input_data is a string, returns the scrambled student ID corresponding to the input string.
            - If input_data is neither a DataFrame nor a string, returns None.

        Notes
        -----
        - The cipher must have exactly 10 characters. If student IDs at your institution have a different number of characters,
          adjust the cipher accordingly.
        - For DataFrames, the 'student_ID' column must be present. If not found, an error message is displayed, and None is returned.
        - Do not post any ciphers publically

        Examples
        --------
        >>> # Scramble a DataFrame of student IDs
        >>> scrambled_df = scramble_ID(dataframe, "abcdefghij")
        >>>
        >>> # Scramble a single student ID string
        >>> scrambled_id = scramble_ID("1234567890", "abcdefghij")
        """

    if len(cipher) != 10: #if student IDs at your institution have different # of characters, then adjust accordingly
        print("The cipher must have 10 characters!")
        return None
    else:
        # Create a dictionary where keys are  string representations of indices
        # and values are the corresponding characters
        scrambleDict = {str(i): char for i, char in enumerate(cipher)}

        # Check if the input is a dataframe
        if isinstance(input_data, pd.DataFrame):
            results_df = input_data.copy()

            # Ensure the 'Student_ID' column is present
            if 'student_ID' not in results_df.columns:
                print("The dataframe does not have a 'student_ID' column.")
                return None

            # Scramble IDs for a dataframe
            results_df["student_ID"] = (
                results_df["student_ID"]
                .astype(str)
                .replace(scrambleDict, regex=True)
            )
            return results_df

        # Check if the input is a string (assuming it's a Student_ID)
        elif isinstance(input_data, str):
            # Scramble ID for a single Student_ID string
            scrambled_id = ''.join(scrambleDict.get(char, char) for char in input_data)
            return scrambled_id

        else:
            print("Input must be a pandas DataFrame or a string representing a student_ID.")
            return None

#[Utility function] accepts a single, scrambled Student_ID and unscrambles it (given the appropriate cipher string)
#Student_ID : string of characters representing the Student_ID to be unscrambled
#cipher : a string of characters length of Student_ID; DON'T FORGET THIS AND DO NOT POST PUBLICALLY
def unscramble_ID(student_ID, cipher):
    """
    Unscramble a student ID based on a cipher.

    Parameters
    ----------
    student_ID : str
        The scrambled student ID to be unscrambled.
    cipher : str
        The cipher used for unscrambling. It should be a string of exactly the same length as the student ID,
        representing the mapping of each character in the scrambled ID to its original digit.

    Returns
    -------
    str or None
        - If the unscrambling is successful, returns the original unscrambled student ID.
        - If the cipher length is not equal to the length of the student ID, returns None.

    Notes
    -----
    - The cipher must have exactly the same length as the student ID. If student IDs at your institution have
      a different number of characters, adjust the cipher accordingly.
    - The function assumes that the provided cipher matches the scrambling performed by the `scramble_ID` function.
    - Do not post any ciphers publically

    Examples
    --------
    >>> original_id = unscramble_ID("abcdefghij", "abcdefghij")
    >>> original_id
    '0123456789'
    """

    if len(cipher) != 10: #if student IDs at your institution have different # of characters, then adjust accordingly
        print("The cipher must have 10 characters!")
        return None
    else:
        # Create a dictionary where keys are  string representations of indices
        # and values are the corresponding characters
        scrambleDict = {str(i): char for i, char in enumerate(cipher)}

    # Scramble IDs. Store code dictionary on different computer than datasets
    unscrambleDict = {char: str(i) for i, char in enumerate(cipher)}

    # Unscramble IDs
    original_id = ''.join([unscrambleDict[char] for char in student_ID])

    return original_id

#[Utility function]  adjust grad_term to give the ending month from a beginning of a grad_term 2023-07-12
def adjust_grad_term(row):
    """
        Adjust the graduation term based on the given month.

        Parameters
        ----------
        row : pandas.Series
            A pandas Series representing a row of data containing a 'month' attribute.

        Returns
        -------
        pandas.Timestamp or pandas.NaT
            The adjusted graduation term as a pandas Timestamp object, or NaT (Not a Timestamp) if the input is NaN.

        Notes
        -----
        - This function adjusts the graduation term based on the month:
            - If the month is January (1), the graduation term is adjusted to May (5).
            - If the month is May (5), the graduation term is adjusted to August (8).
            - If the month is August (8), the graduation term is adjusted to December (12).
            - For any other month, the graduation term remains unchanged.
        - If the input row is NaN (Not a Number), representing missing or undefined data, the function returns NaT.

        Examples
        --------
        >>> import pandas as pd
        >>> adjust_grad_term(pd.Series({'month': 1}))
        Timestamp('NaT')

        >>> adjust_grad_term(pd.Series({'month': 5}))
        Timestamp('NaT')

        >>> adjust_grad_term(pd.Series({'month': 8}))
        Timestamp('NaT')

        >>> adjust_grad_term(pd.Series({'month': 10}))
        Timestamp('NaT')
        """

    if pd.isna(row):  # This checks for NaN values
        return pd.NaT
    if row.month == 1:
        return row.replace(month=5)
    elif row.month == 5:
        return row.replace(month=8)
    elif row.month == 8:
        return row.replace(month=12)
    else:
        return row

#[Utility function] produce a list of semesters given a list of a year or years (created 2023-07-13; updated 2023-07-17)
#defaults to academic semester codes, but calendar_year flag can be set to True as alternative
def create_semesters(years, calendar_year = False):
    """
    Generate a list of semester codes based on the given years.

    Parameters
    ----------
    years : list of int
        A list containing the academic years for which semester codes will be generated.
    calendar_year : bool, optional
        Indicator for whether the academic year aligns with the calendar year (default is False).

    Returns
    -------
    list of int
        A sorted list of semester codes corresponding to the input academic years.

    Notes
    -----
    - This function generates semester codes based on academic years and returns them as a sorted list.
    - By default, the function assumes that the academic year starts in the fall and ends in the summer of the following year.
    - If 'calendar_year' is True, the function assumes that the academic year aligns with the calendar year, with spring starting in January, summer starting in May, and fall starting in August.

    Examples
    --------
    >>> create_semesters([2022, 2023])
    [202108, 202201, 202205, 202208, 202301, 202305]

    >>> create_semesters([2022, 2023], calendar_year=True)
    [202101, 202105, 202108, 202201, 202205, 202208, 202301, 202305, 202308]
    """

    semesters = list()

    if calendar_year:
        for year in years:
            spring = year * 100 + 1
            summer = year * 100 + 5
            fall = year * 100 + 8
            semesterList = list([spring,summer, fall])
            semesters = semesters + semesterList
            semesters.sort()
        return semesters

    else:
        for year in years:
            spring = year * 100 + 1
            summer = year * 100 + 5
            fall = (year-1) * 100 + 8
            semesterList = list([spring,summer, fall])
            semesters = semesters + semesterList
            semesters.sort()
        return semesters

#[Utility function] produce a list of semesters given a list of a year or years (created 2023-07-13; updated 2023-07-17)
#defaults to academic semester codes, but calendar_year flag can be set to True as alternative
def increment_semester(semester_input):
    """
    Increment the given semester code to the next semester.

    Parameters
    ----------
    semester_input : int
        The current semester code (e.g., 202201 for Spring 2022).

    Returns
    -------
    int
        The semester code for the next semester.

    Notes
    -----
    This function increments the given semester code to the next semester, following the academic calendar.
    """

    year_code = str(semester_input)[:4]
    semester_code = str(semester_input)[4:]
    if(semester_code == '08'):
        year_code = str(int(year_code) + 1)
        semester_code = '01'
    elif(semester_code == '01'):
        semester_code = '05'
    else:
        semester_code = '08'
    return year_code + semester_code

# [Utility function] Converts letter grade to numeric value; adjust GPA values to match institution
#ported from R utility_functions_v2 using ChatCPT 3.5
def num_grade_institutional(grade):
    simp = -1
    #grade = grade.replace("^R", "")  # Remove the ^R suffix from the grade; At Georgia State University ^R indicates this grade that was replaced later when a student repeated the course and earned a higher grade

    if grade is None:
        return simp
    # Code all types of withdrawals as -1
    if 'W' in grade:
        return simp

    # Manage situations where the transfer indicator (%), academic renewal indicator (#), dishonesty indicator (@), repeat to replace indicator (^R) and asterisk (*)are present
    if re.search(r'[#%*@^R]', grade):
        grade = re.sub(r'[#%*@^R]', '', grade)

    if grade == "A+":
        simp = 4.33
    elif grade == "A":
        simp = 4
    elif grade == "A-":
        simp = 3.67
    elif grade == "B+":
        simp = 3.33
    elif grade == "B":
        simp = 3
    elif grade == "B-":
        simp = 2.67
    elif grade == "C+":
        simp = 2.33
    elif grade == "C":
        simp = 2
    elif grade == "C-":
        simp = 1.67
    elif grade == "D":
        simp = 1
    elif grade == "F":
        simp = 0
    elif grade == 'IP': #in progress
        simp = -2
    elif grade == 'GP': #grade pending
        simp = -2
    elif grade == 'GH': #unknown letter grade designation
        simp = -2
    elif grade == 'I': #incomplete
        simp = -2
    elif grade == 'nan':  # letter grade designation is listed as 'nan' string in data from our data pull
        simp = -2
    return simp

# [Utility function] Normalizes numeric grade to 4.00 for cross-institution comparison
# ported on 20230717 from R utility_functions_v2 using ChatCPT 3.5
def num_grade_normalized(num_grade, institutional_max):
    """
    Normalize a numeric grade to a 4.00 scale for cross-institutional comparison.

    Parameters
    ----------
    num_grade : int or float
        The numeric grade to be normalized.
    institutional_max : int or float
        The maximum grade allowed by the institution.

    Returns
    -------
    float
        The normalized grade on a 4.00 scale.

    Notes
    -----
    This function normalizes a numeric grade to a 4.00 scale for cross-institutional comparison.
    """

    grade_normalized = -1  # default to a -1 numeric grade

    # If num_grade or institutional_max is invalid, return -1 flag
    if (
        num_grade is None
        or num_grade == -1
        or not isinstance(num_grade, (int, float))
        or institutional_max == -1
        or not isinstance(institutional_max, (int, float))
    ):
        return grade_normalized
    elif institutional_max == -1 or not isinstance(institutional_max, (int, float)) or num_grade > institutional_max:
        return grade_normalized

    grade_normalized = 4 * num_grade / institutional_max  # This normalizes to a 4.00
    return grade_normalized

#Utility function: eliminates +/- distinction and various grade indicators
# developed 20230718 with assistance by ChatGPT3.5
#c_minus_flag is available if the C- grade typically is not passing (as at GSU)
#c_minus_flag = 1 --> C- = D
#c_minus_flag = 0 --> C- = C
def letter_grade_simplify(dataframe, c_minus_flag = True):
    """
    Simplify letter grades by eliminating distinctions and various grade indicators.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The DataFrame containing the column 'course_grade_letter' with letter grades to be simplified.
    c_minus_flag : int, optional
        Flag indicating whether to consider C- as a non-passing grade (D) (default is True).

    Returns
    -------
    pandas.DataFrame
        A copy of the input DataFrame with simplified letter grades.

    Notes
    -----
    This function simplifies letter grades by eliminating distinctions and various grade indicators.
    It optionally treats C- as a passing grade based on the value of 'c_minus_flag'.
    """

    if(c_minus_flag == False):
        grade_mapping = {
            "A+": "A",
            "A-": "A",
            "B+": "B",
            "B-": "B",
            "B*": "B",
            "C+": "C",
            "C*": "C",
            "C-": "C",
            "C-%": "C",
            "D+": "D",
            "D-": "D",
            "D*": "D",
            "FSA": "F",
            "F*": "F",
            "F^R": "F",
            "WF": "F",
            "IF*": "F",
            "IF": "F",
            "UF": "F",
            "W*": "W",
            "-W": "W",
            "WM": "W"
            #WM = military withdrawal
            #V = audit
            #N = continuing education grade (Perimeter College, legacy grade?)
            #@ suffix = dishonesty
            #% suffix = [don't know]
            ## suffix = ]don't know]
        }

    elif (c_minus_flag == True):
        grade_mapping = {
            "A+": "A",
            "A-": "A",
            "B+": "B",
            "B-": "B",
            "B*": "B",
            "C+": "C",
            "C*": "C",
            "C-": "D",
            "C-%": "D",
            "D+": "D",
            "D-": "D",
            "D*": "D",
            "FSA": "F",
            "F*": "F",
            "F^R": "F",
            "WF": "F",
            "IF*": "F",
            "IF": "F",
            "UF": "F",
            "W*": "W",
            "-W": "W",
            "WM": "W"
            # WM = military withdrawal
            # V = audit
            # N = continuing education grade (Perimeter College, legacy grade?)
            # @ suffix = dishonesty
            # % suffix = [don't know]
            ## suffix = ]don't know]
        }

    df_copy = dataframe.copy()
    df_copy['course_grade_letter_simp'] = df_copy['course_grade_letter'].apply(lambda grade: re.sub(r'[%\^R#@*]', '', str(grade)))
    df_copy['course_grade_letter_simp'] = df_copy['course_grade_letter_simp'].map(grade_mapping).fillna(df_copy['course_grade_letter_simp'])

    return df_copy

#Utility function: gets user input on which CSV grades reports files to load and returns as a pandas dataframe
def load_grades():
    """
    Load a CSV grades report file selected by the user and return it as a pandas DataFrame.

    Returns
    -------
    pandas.DataFrame
        The DataFrame containing the grades data loaded from the selected CSV file.

    Notes
    -----
    This function prompts the user to select a CSV grades report file, loads the file as a pandas DataFrame,
    and returns the DataFrame.
    """

    csv_filename = fd.askopenfilename(title = 'Please select the grades file') # show an "Open" dialog box and return the path to the selected file
    print(csv_filename)
    grades_df = pd.read_csv(csv_filename)
    return grades_df


def demographics_first_semester(df, transfer = 0, return_dataframe = 1):
    """
    Get the demographics of students in their first semester.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing demographics data.
    transfer : int, optional
        Flag indicating whether to include students with transfer credits.
        - 0: Include all students.
        - 1: Include only students with transfer credits.
        - 2: Include only students without transfer credits. (default is 0)
    return_dataframe : int, optional
        Flag indicating the format of the output.
        - 1: Return DataFrame containing first semester demographics.
        - 0: Return list of student IDs. (default is 1)

    Returns
    -------
    pandas.DataFrame or list
        DataFrame containing first semester demographics for selected students,
        or list of student IDs depending on the value of return_dataframe.

    Notes
    -----
    - Since 'term_matriculation' is not always exactly matched to the first term a student takes courses,
      the DataFrame is sorted to find the first demographics term for each student.
    """

    # Get the earliest term for each student
    mask = df.groupby('student_ID')['demographics_term'].idxmin()
    earliest_df = df.loc[mask]

    # return dataframe containing first semester demographics for ALL students
    if (transfer == 0):
        if return_dataframe == 1:
            return earliest_df
        elif return_dataframe == 0:
            return list(earliest_df['student_ID'])

    # return dataframe containing first semester demographics for students who WITH transfer credit
    elif (transfer == 1):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['SDSTUMAIN_TRANSFER_HOURS'] > 0) & (~earliest_df['SDSTUMAIN_TRANSFER_HOURS'].isna())]
        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['student_ID'])

    # return dataframe containing first semester demographics for students WITHOUT transfer credit
    elif (transfer == 2):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['SDSTUMAIN_TRANSFER_HOURS'].isna()) | (earliest_df['SDSTUMAIN_TRANSFER_HOURS'] == 0)]

        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['student_ID'])


"""""
Function Name: descriptive_course_stats
Author: Paul Ulrich
Date: 2024/01/29

Description:
    This function generates a summary of descriptive statistics for courses taken by students, 
    with the ability to filter by specific courses, majors, attempts, semesters, and associate flags. 
    It calculates the count and proportion of students by major, the average grade excluding certain values, 
    and demographic proportions such as first-generation college status, gender, and Pell Grant eligibility.

Parameters:
    df (DataFrame): The input DataFrame containing course and student data.
    courses (list of str, optional): A list of course codes to include in the analysis. Defaults to all courses if None.
    majors (list of str, optional): A list of majors to filter the analysis. Defaults to None, which includes all majors.
    all_attempts (bool, optional): When set to True, considers all attempts for the course; 
                                   when False, considers only the first attempt. Defaults to None, which uses the default behavior.
    start_semester (int, optional): The starting semester code (in YYYYMM format) to filter the analysis. Defaults to None.
    end_semester (int, optional): The ending semester code (in YYYYMM format) to filter the analysis. Defaults to None.
    associates (bool, optional): When set to True, includes courses marked with a flag in the 'flag_course_PC' field; 
                                 when False, excludes these courses. Defaults to False.

Returns:
    DataFrame: A summary DataFrame with the following columns: 'COURSE', 'Major_Matriculation', 'Student_Count', 
               'Proportion_Total', 'Average_Num_GRDE', 'Proportion_First_Gen', 'Proportion_Female', 
               and 'Proportion_Pell_Eligible'.

Example Usage:
    courses = ['CHEM1211K', 'CHEM1212K']
    results = descriptive_course_stats(
        df=math_chem_df, 
        courses=courses, 
        majors=['BIO', 'CHM'], 
        start_semester=202201, 
        end_semester=202205
    )
    print(results)
"""
def descriptive_course_stats(df, courses=None, majors= None, all_attempts=False, start_semester=None, end_semester=None, associates = False, exclude_honors = True, return_dataframe = True):
    """
      Generate descriptive statistics for student performance in specified courses while providing the option to exclude honors courses and filter by course, major, semester, and other criteria. This function also allows specifying whether to consider all course attempts or only the first attempt for each student and whether to include courses taken as part of associate degree programs.

      Parameters
      ----------
      df : pandas.DataFrame
          DataFrame containing student course data.
      courses : list of str, optional
          Course codes to include in the analysis. Analyzes all courses if None.
      majors : list of str, optional
          Major codes to filter the data. Includes all majors if None.
      all_attempts : bool, optional
          True to include all attempts; considers only the first attempt if False or None.
      start_semester : int, optional
          The starting semester code (YYYYMM format) for filtering data. Uses the minimum available semester if None.
      end_semester : int, optional
          The ending semester code (YYYYMM format) for filtering data. Uses the maximum available semester if None.
      associates : bool, optional
          True to include associate courses; excludes them if False.
      exclude_honors : bool, optional
          True to exclude honors courses based on titles starting with 'HON' or 'hon'; includes all courses if False.

      Returns
      -------
      pandas.DataFrame
          A DataFrame with descriptive statistics for each course, including counts, proportions, average grades, demographic information, course titles, and the sampling period.

      Examples
      --------
      >>> stats_df = descriptive_course_stats(df=student_df, courses=['CHEM1211K', 'CHEM1212K'], majors=['BIO', 'CHM'], start_semester=202201, end_semester=202205)
      >>> print(stats_df)
      """

    df = df.copy()

    # default behavior excludes honors courses from analysis
    if exclude_honors == True:
        honors_regex = "(?i)HON"
        mask = ~df['course_title'].str.contains(honors_regex,regex=True,na=False)
        df = df[mask]

    # default behavior excludes associates level from analysis
    if associates == False:
        df = df[df['flag_course_PC'] == 0]

    # Set sampling period if not provided.
    if start_semester is None:
        start_semester = df['course_term'].min()
    if end_semester is None:
        end_semester = df['course_term'].max()

    # Create sampling period string
    sampling_period = f"{start_semester} - {end_semester}"

    # create full course number codes
    df['course_fullcode'] = df['course_prefix'] + df['course_number'].astype(str) + df['course_suffix'].fillna('')
    if courses is None:
        courses = df['course_fullcode'].unique()

    if not all_attempts:
        # Keep only the first attempt for each student_ID
        df.sort_values(by=['student_ID', 'course_term'], inplace=True)
        df = df.drop_duplicates(subset=['student_ID', 'course_fullcode'], keep='first')

    # create a dataframe to hold the descriptive results
    results = pd.DataFrame(columns=['course', 'course_fullcode', 'major_matriculation', 'sampling_period', 'sample_size'])

    # filter the dataframe for majors and time range
    if majors:
        df = df[df['major_matriculation'].isin(majors)]
    if start_semester:
        df = df[df['course_term'] >= start_semester]
    if end_semester:
        df = df[df['course_term'] <= end_semester]

    # calculate descriptives for each of the courses in the dataframe
    for course in courses:
        course_df = df[df['course_fullcode'] == course].copy()

        # if  no students are in the dataframe, skip this course
        if course_df.empty:
            continue

        # Add 'course_title' to 'major_counts' by getting the first 'course_title' for the current 'course_fullcode'
        course_title = course_df['course_title'].iloc[0]  # Assumes that all 'course_title' associate with the same 'course_fullcode' are synonymous

        # Tabulate absolute numbers of students by major at matriculation
        major_counts = course_df.groupby('major_matriculation').size().reset_index(name='sample_size')
        major_counts['sampling_period'] = sampling_period  # Add sampling period to the DataFrame
        major_counts['course_fullcode'] = course

        #Calculate proportion the current major is of the total students in the course
        if len(majors) > 1:
            major_counts['Proportion_Total'] = (major_counts['sample_size'] / major_counts['sample_size'].sum()).round(2)

        # Calculate average numerical grade in the course, excluding oddball grades (coded as -2) and withdrawals (coded as -1)
        valid_grades = course_df[course_df['course_grade_numeric'] >= 0].copy()
        avg_grade = valid_grades.groupby('major_matriculation')['course_grade_numeric'].mean().round(2).reset_index(name='course_grade_average')
        major_counts = major_counts.merge(avg_grade, on='major_matriculation', how='left')

        # Calculate proportion of first generations students in the course
        proportion_first_gen = course_df.groupby('major_matriculation')['flag_first_generation'].mean().round(2).reset_index(name='proportion_first_gen')
        major_counts = major_counts.merge(proportion_first_gen, on='major_matriculation', how='left')
        #major_counts.rename(columns={'flag_first_generation': 'First_Gen'}, inplace=True)

        # Calculate Proportion_Female
        proportion_female = course_df[~(course_df['flag_sex'] < 0)] #non-binary sex codes too infrequent and not included, though code can be amended if this changes
        proportion_female = proportion_female.groupby('major_matriculation')['flag_sex'].mean().round(2).reset_index(name='proportion_female')
        major_counts = major_counts.merge(proportion_female, on='major_matriculation', how='left')
        #major_counts.rename(columns={'flag_sex': 'Female'}, inplace=True)

        # Calculate Proportion_Pell_Eligible
        proportion_pell_eligible = course_df.groupby('major_matriculation')['flag_PELL'].mean().round(2).reset_index(name='proportion_pell_eligible')
        major_counts = major_counts.merge(proportion_pell_eligible, on='major_matriculation', how='left')
        #major_counts.rename(columns={'flag_PELL': 'Pell_Eligible'}, inplace=True)

        # Calculate Proportion_PEER (note that self-identification that is more than one race but provides no specifics on race are not included in calculation of proportion)
        proportion_PEER = course_df[course_df['flag_PEER'].isin([0,1])]
        proportion_PEER = proportion_PEER.groupby('major_matriculation')['flag_PEER'].mean().round(2).reset_index(name='proportion_PEER (undefined, more than one race not included)')
        major_counts = major_counts.merge(proportion_PEER, on='major_matriculation', how='left')
        #major_counts.rename(columns={'flag_PEER': 'PEER'}, inplace=True)

        # Calculate Proportion_DFW
        proportion_DFW = course_df.groupby('major_matriculation')['course_grade_letter_simp'].apply(
            lambda x: (x.isin(['D', 'F', 'W']).sum()) / len(x)).round(2).reset_index(name='proportion_DFW')
        major_counts = major_counts.merge(proportion_DFW, on='major_matriculation', how='left')

        major_counts['course'] = course_title
        major_counts = major_counts.sort_values(by='sample_size', ascending=False)
        results = pd.concat([results, major_counts])

    if return_dataframe: return results, df
    else: return results

def calculate_deltas(df):
    """
    Calculate the difference (delta) in mean course grades and DFW rates between
    groups within a segment, specifically focusing on the group where `segment_value == 1`
    against the overall population or another specified group.

    This function assumes that the input DataFrame `df` includes pre-computed statistics
    (mean and DFW rates) for each segment and that these calculations are intended
    to be performed where the `segment_value == 1`.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame with pre-computed mean and DFW rate statistics for a specific
        segment of interest. It should contain rows for segment values, including
        mean grades and DFW rates, to allow for delta calculations.

    Returns
    -------
    tuple
        A tuple containing two elements: the delta in mean grades (`delta_mean`)
        and the delta in DFW rates (`delta_dfw`) between the specified group
        (`segment_value == 1`) and the reference group or population.

    Notes
    -----
    The function is designed to work with data where segment analyses have been
    pre-aggregated. It expects the input DataFrame to include specific columns:
    `mean` for the average grades and `proportion_DFW` for the DFW rates.

    Created using ChatGPT 4.0 (Ulrich, 2024-04-01)
    """


    if df.empty or len(df) < 2:
        return 0, 0  # Return default deltas if insufficient data

    # Ensure the DataFrame is sorted by segment value to guarantee alignment
    df = df.sort_values(by='segment_value')

    # Calculate deltas
    delta_mean = round(df.iloc[1]['mean'] - df.iloc[0]['mean'], 2)  # 1's mean - 0's mean
    delta_dfw = round(df.iloc[1]['proportion_DFW'] - df.iloc[0]['proportion_DFW'], 2)  # 1's DFW - 0's DFW

    return delta_mean, delta_dfw

def calculate_gaps_in_course_grades(df, courses=None, majors=None, all_attempts=False,
                                    start_semester=None, end_semester=None,
                                    associates=False, exclude_honors=True):
    """
    Calculate gaps in course_grade_numeric (mean ± 1 standard deviation) and
    delta DFW (Drop, Fail, Withdraw) rates for students, segmented by gender (flag_sex),
    race/ethnicity (flag_PEER), and Pell Grant eligibility (flag_PELL), considering
    various filtering options. This function aims to highlight disparities in academic
    performance and outcomes across different demographic groups within the dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing student course data, including demographics and grade outcomes.
    courses : list of str, optional
        Specific course titles to include in the analysis. Analyzes all courses if None.
    majors : list of str, optional
        Specific major codes to filter the data. Includes all majors if None.
    all_attempts : bool, optional
        If True, include all course attempts by a student; if False, considers only the
        first attempt.
    start_semester : int, optional
        The starting semester code (YYYYMM format) for filtering data. Analyzes from
        the earliest semester available if None.
    end_semester : int, optional
        The ending semester code (YYYYMM format) for filtering data. Analyzes up to
        the latest semester available if None.
    associates : bool, optional
        If True, include courses taken as part of associate degree programs; otherwise,
        excludes them.
    exclude_honors : bool, optional
        If True, exclude honors courses from the analysis; includes all courses if False.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the calculated grade gaps (mean ± 1 standard deviation)
        and delta DFW rates, with each row representing a different demographic
        segment for the selected courses. This version focuses on differences where
        `segment_value == 1`, highlighting disparities for these groups specifically.

    Notes
    -----
    - The function includes optional filtering capabilities to refine the analysis based
      on course, major, attempt status, semester range, associate degree inclusion,
      and the exclusion of honors courses.
    - Deltas are calculated to highlight differences in performance for segments where
      `segment_value == 1`, offering insights into specific disparities within the dataset.
    - Created in conjunction with ChatGPT 4.0 (Ulrich, 2024-04-01)
    """
    df = df.copy()

    # Apply filters based on parameters
    if exclude_honors:
        df = df[~df['course_title'].str.contains('HON', case=False, na=False)]

    if not associates:
        df = df[df['flag_course_PC'] == 0]

    if start_semester is not None:
        df = df[df['course_term'] >= start_semester]

    if end_semester is not None:
        df = df[df['course_term'] <= end_semester]

    if majors is not None:
        df = df[df['major_matriculation'].isin(majors)]

    if courses is not None:
        df = df[df['course_title'].isin(courses)]

    # create full course number codes
    df['course_fullcode'] = df['course_prefix'] + df['course_number'].astype(str) + df['course_suffix'].fillna('')

    if not all_attempts:
        df.sort_values(by=['student_ID', 'course_term'], inplace=True)
        df = df.drop_duplicates(subset=['student_ID', 'course_fullcode'], keep='first')

    # Utilize only binary flag_sex since non-binary (coded as -2) are so rare
    # TODO : modify setup_demographic_flags() with  logic for situations where non-binary codes are utilized
    df = df[df['flag_sex'] >=0]

    # If more than one race reported, then do not include
    # TODO : modify setup_demographic_flags() to address situations where more than one race reported but still PEER
    df = df[df['flag_PEER'].isin([0,1])]

    # Exclude withdrawals and odd situations from course_grade_numeric calculations
    # df_valid_grades = df[df['course_grade_numeric'] >= 0]

    # Segments to analyze
    segments = ['flag_sex', 'flag_PEER', 'flag_PELL']
    all_results = []

    for course in courses:
        course_df = df.copy()
        course_df = course_df[course_df['course_title'] == course]

        # Exclude withdrawals and odd situations from course_grade_numeric calculations
        course_valid_grades_df = course_df[course_df['course_grade_numeric'] >= 0]

        # Create a column that flags DFW's
        course_df['flag_DFW'] = course_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])

        results = []

        for segment in segments:
            # Calculate mean and standard deviation of course grades for each segment
            segment_grade_stats = course_valid_grades_df.groupby(segment)['course_grade_numeric'].agg(['mean', 'std']).reset_index()
            segment_grade_stats['mean'] = segment_grade_stats['mean'].round(2)
            segment_grade_stats['std'] = segment_grade_stats['std'].round(2)

            # Calculate proportion of DFW grades for each segment
            proportion_DFW = course_df.groupby(segment)['flag_DFW'].mean().round(2).reset_index(name='proportion_DFW')

            # Merge grade stats with DFW proportions
            segment_results = pd.merge(segment_grade_stats, proportion_DFW, on=segment)
            segment_results.rename(columns={segment: 'segment_value'}, inplace=True)

            delta_mean, delta_dfw = calculate_deltas(segment_results)
            segment_results['delta_mean_grade'] = delta_mean
            segment_results['delta_DFW_rate'] = delta_dfw

            # Prepare the segment stats for merging
            segment_results['segment'] = segment
            segment_results['course'] = course
            results.append(segment_results)

        course_results = pd.concat(results, ignore_index=True)
        all_results.append(course_results)

    # Concatenate results for all courses
    results_df = pd.concat(all_results, ignore_index=True)
    # Explicitly rearrange columns for output to have 'segment' as the first column
    results_df = results_df[['course', 'segment', 'segment_value', 'mean', 'std', 'delta_mean_grade', 'proportion_DFW', 'delta_DFW_rate']]

    return results_df

def rename_columns_in_bulk(df, column_mapping_filepath):
    """
    Rename columns in a DataFrame in bulk based on a column mapping extracted from an Excel file.

    Parameters
    ----------
    df : pandas DataFrame
        The DataFrame whose columns are to be renamed.
    column_mapping_filepath : str
        The file path to the tab-delimited file containing the column mapping.

    Returns
    -------
    pandas DataFrame
        The DataFrame with renamed columns.

    Notes
    -----
    This function reads an Excel file (.xls or .xlsx) containing two sheets: a description sheet with information,
    on the file and a sheet detailing the column mapping. The function extracts the mapping, flattens
    the nested column mapping dictionary, and renames the columns of the input DataFrame accordingly.

    The column mapping file must include three columns: 'variable_name_project', 'variable_name_institution',
    and 'description', where 'variable_name_project' corresponds to the old column names and
    'variable_name_institution' corresponds to the new column names.

    Example usage:
    ```python
    df = pd.DataFrame(...)  # Define your DataFrame
    renamed_df = rename_columns_in_bulk(df, 'path/to/column_mapping_file.xlsx')
    ```

    """
    # Extract column mapping from the file and flattened the nested column mapping dictionary
    column_mapping_nested = extract_column_mapping(column_mapping_filepath)
    column_mapping_flattened = flatten_column_mapping(column_mapping_nested)

    # Convert any list-like column names to string values
    column_mapping_str = {k: v[0] if isinstance(v, list) else v for k, v in column_mapping_flattened.items()}

    return df.rename(columns=column_mapping_str)


def extract_column_mapping(file_path):
    """
    Extract column mapping from an Excel file (.xlsx or .xls)

    Parameters
    ----------
    file_path : str
        Path to the Excel spreadsheet file containing column mapping.

    Returns
    -------
    dict
        A dictionary where keys are variable_name_project values and values are lists of variable_name_institution values.
    """
    column_mapping = {}
    df = pd.read_excel(file_path, sheet_name = 'codebook', engine = 'openpyxl')
    for index, row in df.iterrows():
        project_name = row['variable_name_project']
        institution_names = str(row['variable_name_institution'])

        if project_name and institution_names:  # Check if the values are not empty
            institution_names = [name.strip() for name in
                                 institution_names.split(',')]  # Split by comma and strip whitespace
            if project_name not in column_mapping:
                column_mapping[project_name] = []
            column_mapping[project_name].extend(institution_names)
    return column_mapping


def flatten_column_mapping(column_mapping):
    """
    Flatten column mapping from a nested dictionary to a single-level dictionary.

    Parameters
    ----------
    column_mapping : dict
        A dictionary where keys are variable_name_project values and values are lists of variable_name_institution values.

    Returns
    -------
    dict
        A flattened dictionary where keys are variable_name_institution values and values are variable_name_project values.
    """
    flattened_mapping = {}
    for project_name, institution_names in column_mapping.items():
        for institution_name in institution_names:
            institution_name = institution_name.strip('[]')  # Strip square brackets
            # Split the institution names if they contain commas
            for name in institution_name.split(','):
                # Strip any leading or trailing whitespace
                name = name.strip()
                # Check if the name is already in the flattened mapping
                if name in flattened_mapping:
                    # If already present, append the project name to the existing list
                    flattened_mapping[name].append(project_name)
                else:
                    # If not present, create a new entry with the project name
                    flattened_mapping[name] = [project_name]
    return flattened_mapping

def set_up_demographic_flags(df, peer = True, pell = True, first_generation = True, sex =True):
    """
    Sets up demographic flags in the given DataFrame based on specified demographic criteria.

    This function conditionally adds several columns to the DataFrame indicating demographic flags for
    first-generation status, PELL grant eligibility, PEER group membership, and sex, based on the boolean
    parameters provided.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to which the demographic flags will be added. It is expected to have columns named
        'demographics_race' and 'demographics_sex', among others, depending on the flags requested.
    peer : bool, optional
        If True, sets up the PEER group flag based on 'demographics_race'. Defaults to True.
    pell : bool, optional
        If True, sets up the PELL grant eligibility flag. Defaults to True.
    gender : bool, optional
        Placeholder for future implementation. Currently does not alter function behavior. Defaults to True.
    first_generation : bool, optional
        If True, sets up the first-generation student flag. Defaults to True.
    sex : bool, optional
        If True, sets up the sex flag based on 'demographics_sex'. Defaults to True.

    Returns
    -------
    pandas.DataFrame
        A copy of the input DataFrame with additional columns for each of the demographic flags requested.

    Examples
    --------
    >>> df = pd.DataFrame({'demographics_race': ['Asian', 'Black or African American', 'White'],
    ...                     'demographics_sex': ['Male', 'Female', np.nan],
    ...                     'flag_first_generation': ['Y', 'N', np.nan]})
    >>> set_up_demographic_flags(df)
    """

    peer_dict = {'American Indian or Alaska Native': 1, 'Asian': 0, 'Black or African American': 1, 'More Than One Race Reported': 2, 'Not Reported': -1, 'White': 0}
    sex_dict = {'Female': 1, 'Male': 0, 'F': 1, 'M': 0, np.nan: -1}

    dataframe_with_flags = df.copy()

    if first_generation:
        dataframe_with_flags['flag_first_generation'].replace({'Y': 1, 'N':0, np.nan: 0}, inplace=True)
    if pell == True:
        dataframe_with_flags['flag_PELL'].replace({'Y': 1, 'N': 0, np.nan: 0}, inplace=True)
        dataframe_with_flags['flag_PELL'] = dataframe_with_flags['flag_PELL'].astype('int')
    if peer == True:
        # Use regex to match specified races in a case-insensitive way
        # Joining the races with '|', which works as an "OR" operator in regex
        races_regex = "(?i)african american|black|american indian|hawaiian|alaska native|native american"

        # Default 'flag_PEER' to 0 to correctly handle 'White' and any other values not matching the regex
        dataframe_with_flags['flag_PEER'] = 0

        # Create a new column 'flag_PEER', set to 1 where 'demographics_race' matches the regex, 0 otherwise
        dataframe_with_flags['flag_PEER'] = dataframe_with_flags['demographics_race'].str.contains(races_regex,
                                                                                                   regex=True,
                                                                                                  na=False).astype(int)
        # Explicitly set specific situations
        dataframe_with_flags.loc[dataframe_with_flags['demographics_race'] == 'Not Reported', 'flag_PEER'] = -1
        dataframe_with_flags.loc[dataframe_with_flags['demographics_race'] == 'More Than One Race Reported', 'flag_PEER'] = 2

    if sex == True:
        dataframe_with_flags['flag_sex'] =  dataframe_with_flags['demographics_sex'].map(sex_dict).fillna(-1) # any values that don't have a corresponding key in sex_dict are coded to -1

    return dataframe_with_flags