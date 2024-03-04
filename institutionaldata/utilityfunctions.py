# Let's write a helper function to adjust the graduation term to the end of the term
import pandas as pd
from tkinter import filedialog as fd
import tkinter as tk
import re

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
def letter_grade_simplify(dataframe, c_minus_flag = 1):
    """
    Simplify letter grades by eliminating distinctions and various grade indicators.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The DataFrame containing the column 'course_grade_letter' with letter grades to be simplified.
    c_minus_flag : int, optional
        Flag indicating whether to consider C- as a passing grade (default is 1).

    Returns
    -------
    pandas.DataFrame
        A copy of the input DataFrame with simplified letter grades.

    Notes
    -----
    This function simplifies letter grades by eliminating distinctions and various grade indicators.
    It optionally treats C- as a passing grade based on the value of 'c_minus_flag'.
    """

    if(c_minus_flag == 0):
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

    elif (c_minus_flag == 1):
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
def descriptive_course_stats(df, courses=None, majors= None, all_attempts=None, start_semester=None, end_semester=None, associates = False):
    """
    Generate descriptive statistics for student performance in specified courses.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing student data.
    courses : list of str, optional
        List of course codes to analyze (default is None, which analyzes all unique courses in the DataFrame).
    majors : list of str, optional
        List of major codes to filter the data by (default is None, which includes all majors).
    all_attempts : bool, optional
        Flag indicating whether to consider all attempts or only first attempts (default is None, which considers only first attempts).
    start_semester : int, optional
        The starting semester code to filter the data by (default is None, which includes all semesters).
    end_semester : int, optional
        The ending semester code to filter the data by (default is None, which includes all semesters).
    associates : bool, optional
        Flag indicating whether to include associate courses (default is False).

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing descriptive statistics for each specified course,
        including student counts, proportions, average grades, and demographic information.

    Notes
    -----
    This function generates descriptive statistics for student performance in specified courses.
    It calculates student counts, proportions, average grades, and demographic information such as
    the proportion of first-generation students, female students, and Pell Grant-eligible students.
    """

    df['COURSE'] = df['COURSE_PREFIX'] + df['COURSE_NUMBER'].astype(str) + df['COURSE_SUFFIX'].fillna("")
    if courses is None:
        courses = df['COURSE'].unique()

    results = pd.DataFrame(columns=['COURSE', 'Major_Matriculation', 'Student_Count', 'Proportion_Total'])

    if majors:
        df = df[df['Major_Matriculation'].isin(majors)]
    if start_semester:
        df = df[df['TERM'] >= start_semester]
    if end_semester:
        df = df[df['TERM'] <= end_semester]

    for course in courses:
        course_df = df[df['COURSE'] == course]

        # Default behavior is to only look at first attempts for the course
        if all_attempts is None:
            earliest_semester = course_df.groupby('Student_ID')['TERM'].min().reset_index()
            # Merge the original DataFrame with the earliest semester information
            course_df = course_df.merge(earliest_semester, on=['Student_ID', 'TERM'], how='inner')

        if associates == False:
            course_df = course_df[course_df['flag_course_PC'] == 0]

        # Tabulate the absolute numbers of students by major at matriculation
        major_counts = course_df.groupby('Major_Matriculation').size().reset_index(name='Student_Count')
        major_counts['COURSE'] = course
        major_counts['Proportion_Total'] = (major_counts['Student_Count'] / major_counts['Student_Count'].sum()).round(3)

        # Calculate the average Num_GRDE, excluding -2 and -1
        valid_grades = course_df[course_df['Num_GRDE'] >= 0]
        avg_grade = valid_grades.groupby('Major_Matriculation')['Num_GRDE'].mean().round(2).reset_index(name='Average_Num_GRDE')
        major_counts = major_counts.merge(avg_grade, on='Major_Matriculation', how='left')

        # Calculate Proportion_First_Gen
        proportion_first_gen = course_df.groupby('Major_Matriculation')['FIRST_GENERATION_IND'].mean().round(2)
        major_counts = major_counts.merge(proportion_first_gen, on='Major_Matriculation', how='left')
        major_counts.rename(columns={'FIRST_GENERATION_IND': 'Proportion_First_Gen'}, inplace=True)

        # Calculate Proportion_Female
        proportion_female = course_df.groupby('Major_Matriculation')['SEX'].mean().round(2)
        major_counts = major_counts.merge(proportion_female, on='Major_Matriculation', how='left')
        major_counts.rename(columns={'SEX': 'Proportion_Female'}, inplace=True)

        # Calculate Proportion_Pell_Eligible
        proportion_pell_eligible = course_df.groupby('Major_Matriculation')['PELL_ELIGIBLE_IND'].mean().round(2)
        major_counts = major_counts.merge(proportion_pell_eligible, on='Major_Matriculation', how='left')
        major_counts.rename(columns={'PELL_ELIGIBLE_IND': 'Proportion_Pell_Eligible'}, inplace=True)

        major_counts = major_counts.sort_values(by='Student_Count', ascending=False)
        results = pd.concat([results, major_counts])

    return results
# Example usage:
# Assuming 'math_chem_df' is your DataFrame and 'courses' is a list of course codes
# courses = ['CHEM1211K', 'CHEM1212K']
# print(descriptive_course_stats(df=math_chem_df, courses=courses, majors= ['BIO', 'CHM'], start_semester=202201, end_semester=202205))


def rename_columns_in_bulk(df, column_mapping_filepath):
    """
    Rename columns in a DataFrame in bulk based on a column mapping extracted from a file.

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
    This function reads a tab-delimited file containing a column mapping, extracts the mapping, flattens
    the nested column mapping dictionary, and renames the columns of the input DataFrame accordingly.

    The column mapping file should have three columns: 'variable_name_project', 'variable_name_institution',
    and 'description', where 'variable_name_project' corresponds to the old column names and
    'variable_name_institution' corresponds to the new column names.

    Example usage:
    ```python
    df = pd.DataFrame(...)  # Define your DataFrame
    renamed_df = rename_columns_in_bulk(df, 'path/to/column_mapping_file.tsv')
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
    Extract column mapping from a tab-delimited file.

    Parameters
    ----------
    file_path : str
        Path to the tab-delimited file containing column mapping.

    Returns
    -------
    dict
        A dictionary where keys are variable_name_project values and values are lists of variable_name_institution values.
    """
    column_mapping = {}
    df = pd.read_csv(file_path, delimiter='\s+', skipinitialspace=True, comment='#')
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