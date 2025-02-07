# Let's write a helper function to adjust the graduation term to the end of the term
import pandas as pd
from tkinter import filedialog as fd
import tkinter as tk
import re
import numpy as np
from datetime import datetime
import string
import os

# 2024-09-03 address upcoming changes for pandas 3 related to downcasting that occurred silently in pandas <3
pd.set_option('future.no_silent_downcasting', True)

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
                .str.lstrip('0')  # Remove leading zeros correctly with .str
                .replace(scrambleDict, regex=True)
            )
            return results_df

        # Check if the input is a string (assuming it's a Student_ID)
        elif isinstance(input_data, str):
            # Scramble ID for a single Student_ID string
            stripped_id = input_data.lstrip('0')  # Remove leading zeros for a single ID
            scrambled_id = ''.join(scrambleDict.get(char, char) for char in stripped_id)
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


def clean_matriculation_term(demographics_df, student_id_col='student_ID', term_col='term_matriculation',
                             demo_term_col='demographics_term'):
    """
    Cleans the DataFrame by identifying and keeping only rows for student_ID's that have a
    demographics term associated with the minimum matriculation term. This avoids issues
    that occur when a dataset for various years includes demographics but the dataset does not go
    back far enough in time to get demographics associated with their first term.

    Parameters:
    - courses_df (pd.DataFrame): DataFrame containing course and student information.
    - student_id_col (str): Column name for student ID.
    - term_col (str): Column name for the term of matriculation.
    - demo_term_col (str): Column name for the demographics term.

    Returns:
    - pd.DataFrame: A cleaned DataFrame containing only the rows where the demographics term
      matches the minimum term of matriculation for each student and at least one valid match exists.
    """
    # Step 1: Determine the minimum 'term_matriculation' for each student
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
    Adjusts the matriculation term to the earliest available demographics term or the minimum
    matriculation term for each student, ensuring inclusion of students who may start studies later.
    """
    # Filter students based on the count of unique matriculation terms, if required
    matriculation_counts = demographics_df.groupby(student_id_col)[matriculation_term_col].nunique()
    if include_multiple_matriculations == 0:
        valid_student_ids = matriculation_counts[matriculation_counts == 1].index
        demographics_df = demographics_df[demographics_df[student_id_col].isin(valid_student_ids)]

    # Get the minimum matriculation term for each student
    min_matriculation_df = demographics_df.groupby(student_id_col)[matriculation_term_col].min().reset_index()
    min_matriculation_df.rename(columns={matriculation_term_col: 'matriculation_term_min'}, inplace=True)
    merged_df = pd.merge(demographics_df, min_matriculation_df, on=student_id_col, how='left')
    print(list(merged_df))

    # If a minimum term is indicated for demographics_range_min, then filter out rows where matriculation occurred
    # before dmographics_range_min
    if demographics_range_min:
        merged_df = merged_df[merged_df['matriculation_term_min'] >= demographics_range_min]
        # merged_df is now the filtered dataset

    # Determine the earliest demographics term for each student and add new column to merged_df
    earliest_demographics_df = merged_df.groupby(student_id_col)[demo_term_col].min().reset_index()
    earliest_demographics_df.rename(columns={demo_term_col: 'earliest_demographics_term'}, inplace=True)
    merged_df = pd.merge(merged_df, earliest_demographics_df, on=student_id_col, how='left')
    print(list(merged_df))

    # Assign the adjusted matriculation term
    merged_df['matriculation_term_adjusted'] = merged_df.apply(
        lambda x: x['matriculation_term_min'] if x['earliest_demographics_term'] == x['matriculation_term_min']
        else x['earliest_demographics_term'], axis=1
    )

    return merged_df

def clean_and_adjust_matriculation_old(demographics_df, student_id_col='student_ID', term_col='term_matriculation',
                                   demo_term_col='demographics_term', include_multiple_matriculations=0,
                                   demographics_range_min=None):
    """
    Cleans the DataFrame by adjusting the demographics to the first available term of study or the minimum
    matriculation term for each student. This avoids selection bias by including students who may defer their
    studies to a later term than their initial matriculation. Optionally excludes students with multiple
    matriculation records and filters out students whose matriculation begins before a specified demographics term.

    Parameters:
    - demographics_df (pd.DataFrame): DataFrame containing demographics and student information.
    - student_id_col (str): Column name for student ID.
    - term_col (str): Column name for the term of matriculation.
    - demo_term_col (str): Column name for the demographics term.
    - include_multiple_matriculations (int): Flag to include students with multiple matriculation terms (1) or exclude them (0).
    - demographics_range_min (int, optional): The earliest acceptable matriculation term for inclusion in the analysis.

    Returns:
    - pd.DataFrame: A cleaned DataFrame containing demographics from the earliest term or from the minimum
      matriculation term for students without demographics from their first term, filtered based on the
      number of matriculation terms and the specified range as specified.
    """
    # Step 1: Determine the unique count of 'term_matriculation' for each student
    matriculation_counts = demographics_df.groupby(student_id_col)[term_col].nunique()

    # Filter based on the include_multiple_matriculations flag
    if include_multiple_matriculations == 0:
        valid_student_ids = matriculation_counts[matriculation_counts == 1].index
        demographics_df = demographics_df[demographics_df[student_id_col].isin(valid_student_ids)]

    # Step 2: Determine the minimum 'term_matriculation' for each student
    min_matriculation_df = demographics_df.groupby(student_id_col)[term_col].min().reset_index()
    min_matriculation_df.rename(columns={term_col: 'term_matriculation_min'}, inplace=True)

    # Step 3: Merge this minimum matriculation back with the original DataFrame
    merged_df = pd.merge(demographics_df, min_matriculation_df, on=student_id_col, how='left')

    # Step 4: Apply the demographic range minimum filter if specified
    if demographics_range_min is not None:
        merged_df = merged_df[merged_df['term_matriculation_min'] >= demographics_range_min]

    # Step 5: Identify the earliest demographics term for each student
    earliest_demographics_idx = merged_df.groupby(student_id_col)[demo_term_col].idxmin()
    earliest_demographics_df = merged_df.loc[earliest_demographics_idx]

    # Merge to ensure all students have the earliest available demographics
    final_df = pd.merge(merged_df, earliest_demographics_df[[student_id_col, demo_term_col, 'SDSTUMAIN_TRANSFER_HOURS']], on=student_id_col, suffixes=('', '_earliest'))

    return final_df

# Example usage:
# cleaned_df = clean_and_adjust_matriculation(demographics_df, demographics_range_min=202001)

def calculate_running_semester_number(demographics_df, student_ID_column='student_ID', term_column='demographics_term'):
    """
    Calculates the running semester number for each student based on their terms in ascending order.

    Parameters:
    - df (pd.DataFrame): DataFrame containing student data.
    - student_id_col (str): Column name for student IDs.
    - term_col (str): Column name for the term or semester.

    Returns:
    - pd.DataFrame: DaditaFrame with an additional column for semester numbers.
    """
    # Sort the DataFrame by 'student_ID' and 'demographics_term' in ascending order
    sorted_df = demographics_df.sort_values(by=[student_ID_column, term_column])

    # Calculate 'semester_number' for each student
    sorted_df['semester_number'] = sorted_df.groupby(student_ID_column).cumcount() + 1

    return sorted_df

# Example usage of the function
# updated_df = calculate_running_semester_number(cleaned_df)

def map_matriculation_major(cleaned_df, student_ID_column='student_ID', demographics_term_column='demographics_term',
                            matriculation_term_column='matriculation_term_min', major_column='major_term',
                            new_column='major_matriculation', flag_column='flag_major_retention'):
    """
    Maps each student's major at the time of their matriculation by finding the earliest
    demographics term that matches their matriculation term and assigning the corresponding major.
    Additionally, calculates a flag indicating whether the student's current major matches the
    major at matriculation.

    Parameters:
    - cleaned_df (pd.DataFrame): DataFrame that has been cleaned by ensuring each student's demographics term matches their minimum matriculation term. This can be performed
      by applying utilityfunctions.clean_matriculation_term()
    - student_ID_column (str): Column name for student ID.
    - demographics_term_column (str): Column name for the demographics term.
    - matriculation_term_column (str): Column name for the minimum term of matriculation.
    - major_column (str): Column name for the major term.
    - new_column (str): New column name where the mapped major will be stored.
    - flag_column (str): New column name for the flag indicating if the current major matches the matriculation major.

    Returns:
    - pd.DataFrame: The input DataFrame with additional columns showing each student's major at matriculation and a retention flag.
    """
    # Filter rows where the demographics term matches the minimum matriculation term
    filtered_df = cleaned_df[cleaned_df[demographics_term_column] == cleaned_df[matriculation_term_column]].copy()

    # Create a map from student ID to major term at the time of matriculation
    major_matriculation_map = filtered_df.set_index(student_ID_column)[major_column]

    # Map the major matriculation back to the original cleaned DataFrame
    cleaned_df.loc[:, new_column] = cleaned_df[student_ID_column].map(major_matriculation_map)

    # Determine if the current major matches the matriculation major
    cleaned_df.loc[:, flag_column] = (cleaned_df[major_column] == cleaned_df[new_column]).astype(int)

    return cleaned_df

# Example usage:
# updated_df = map_matriculation_major(cleaned_df)

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

import pandas as pd
import numpy as np
from datetime import datetime

def get_academic_year(term_code):
    """
    Get the academic year for a given term code (YYYYMM).

    Parameters
    ----------
    term_code : int, numpy integer, or datetime
        The term code representing the year and month (YYYYMM).

    Returns
    -------
    int
        The academic year corresponding to the given term code.

    Notes
    -----
    The academic year starts in the fall of the previous calendar year (August, YYYY08)
    and ends in the summer of the following year (May, YYYY05).
    For example, the academic year 2006 includes fall 200508, spring 200601, and summer 200605.

    Developed with ChatGPT4o, 2024-10-14 (PNU)
    """

    # If term_code is a datetime, extract year and month
    if isinstance(term_code, (pd.Timestamp, datetime)):
        year = term_code.year
        month = term_code.month
    elif isinstance(term_code, (int, np.integer)):  # Handle both Python int and NumPy int
        # Extract year and month from YYYYMM format
        year = int(term_code) // 100  # Ensure conversion to Python int
        month = int(term_code) % 100
    else:
        raise ValueError("term_code must be an int in YYYYMM format, a NumPy integer, or a datetime object")

    # Determine academic year based on the month of the term code
    if month == 8:  # Fall term
        return year + 1
    elif month in {1, 5}:  # Spring or Summer term
        return year
    else:
        raise ValueError("term_code must represent a valid academic month (01, 05, 08)")



def get_nth_year_fall_term(term_series, years=3, return_as_datetime=True):
    """
    Calculate the term code for the Fall semester of the N-th year based on the initial term code series.

    Parameters
    ----------
    term_series : pd.Series or pd.DatetimeIndex
        A Series of initial term codes in YYYYMM format or datetime format.
    years : int, optional
        The number of years after the initial term code to calculate the Fall term code for. Default is 3 years.
    return_as_datetime : bool, optional
        If True (default), return the Fall semester term as a datetime object. If False, return it as an integer in YYYYMM format.

    Returns
    -------
    pd.Series
        A Series of term codes for the Fall semester of the N-th year in either datetime or YYYYMM format.

    Examples
    --------
    >>> sample_series_yyyymm = pd.Series([201008, 201101, 201105])
    >>> get_nth_year_fall_term(sample_series_yyyymm, years=3)
    0   2013-08-01
    1   2014-08-01
    2   2014-08-01
    dtype: datetime64[ns]

    >>> get_nth_year_fall_term(sample_series_yyyymm, years=3, return_as_datetime=False)
    0    201308
    1    201408
    2    201408
    dtype: int64
    """

    if isinstance(term_series, pd.DatetimeIndex):
        term_series = pd.Series(term_series)

    if pd.api.types.is_datetime64_any_dtype(term_series):
        # Convert datetime to YYYYMM format
        initial_year = term_series.dt.year
        initial_month = term_series.dt.month
    else:
        # Extract the year and term part from the initial term code
        initial_year = term_series // 100
        initial_month = term_series % 100

    # Calculate the starting academic year based on the initial term
    start_year = initial_year - (initial_month != 8)

    # Calculate the year for the Fall semester of the N-th year
    nth_year_fall_year = start_year + years

    # Construct the term code for the Fall semester of the N-th year
    nth_year_fall_term_code = nth_year_fall_year * 100 + 8

    if return_as_datetime: #default behavior returns datetime and avoid dtype incompatibility issues when used
        # Return as datetime object
        return pd.to_datetime(nth_year_fall_term_code.astype(str), format='%Y%m')

    else:
        # Return as int64 (YYYYMM format)
        return pd.Series(nth_year_fall_term_code,
                         index=term_series.index if isinstance(term_series, pd.Series) else None)

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
    """
    Converts a grade string into its corresponding numeric value based on institutional grading policies.

    Parameters
    ----------
    grade : str or float
        The grade value to be processed. This can include standard letter grades
        (e.g., "A", "B+"), special grades (e.g., "IP", "WM", "S", "U"), or values with suffixes
        (e.g., "A%", "C*"). Missing values or NaN are also supported.

    Returns
    -------
    float
        The numeric value corresponding to the grade. Possible return values include:
        - Positive numeric values (e.g., 4.33 for "A+", 3.33 for "B+")
        - -1 for withdrawals or unrecognized grades
        - -2 for special cases such as:
            * Grades with specific suffixes like "%", "@", "*", "^R", "#"
            * Grades like "IP", "GH", "GP", "I" (e.g., in-progress or incomplete)
            * Military withdrawals ("WM")
        - -2 for audits and continuing education ("V" or "N" in the grade)
        - -3 for pass/fail course grades ("S" or "U")

    Notes
    -----
    - The function handles both standard and non-standard grades, including:
        * Withdrawals ("W", "WF", "W%") are coded as -1, except "WM" (military withdrawal), which is coded as -2.
        * Pass/fail grades ("S", "U") are coded as -3.
        * Special characters (% # @ ^R *) are removed before processing the grade.
    - Missing or null values (NaN, None) are returned as -1.
    - Letter grades with valid numeric equivalents (e.g., "A", "B+", "C") are mapped directly.

    Examples
    --------
    >>> num_grade_institutional("A+")
    4.33
    >>> num_grade_institutional("B-")
    2.67
    >>> num_grade_institutional("W")
    -1
    >>> num_grade_institutional("WM")
    -2
    >>> num_grade_institutional("S")
    -3
    >>> num_grade_institutional(None)
    -1
    >>> num_grade_institutional("C*")
    2.0

    """

    # by default, unknown or missing situations will be coded as -1
    simp = -1
    #grade = grade.replace("^R", "")  # Remove the ^R suffix from the grade; At Georgia State University ^R indicates this grade that was replaced later when a student repeated the course and earned a higher grade

    if pd.isnull(grade):
        return simp

    # Code all types of withdrawals as -1 except military withdrawals
    if grade == 'WM':
        return -2
    if 'W' in grade:
        return simp

    # code audits and continuing ed as a miscellaneous category (-2)
    if 'V' in grade or 'N' in grade:
        return -2

    # code pass/fail course grades as -3
    if 'S' in grade or 'U' in grade:
            return -3

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
            "WM": "W",
            "PW": "W"
            #GP = grade pending (typically during dishonesty charge process)
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
            "W": "W",
            "W*": "W",
            "-W": "W",
            "WM": "W",
            "PW": "W"
            # GP = grade pending (typically during dishonesty charge process)
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


#Utility function: eliminates various distinctions in letter grades but retains plus/minus
# developed 20241206
def letter_grade_clean(dataframe):
    """
    "Purify" the letter grades by eliminating eliminating distinctions and various grade indicators.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The DataFrame containing the column 'course_grade_letter' with letter grades to be simplified.

    Returns
    -------
    pandas.DataFrame
        A copy of the input DataFrame with cleaned up letter grades.

    Notes
    -----
    Developed 2024-12-06 by Paul Ulrich because grades were being missed in calculus analyses if a student did repeat to replace or had some other not grade distinction
    listed. This was creating problems with ordered categories.
    """
    df_copy = dataframe.copy()
    df_copy['course_grade_letter'] = df_copy['course_grade_letter'].apply(lambda grade: re.sub(r'[%\^R#@*]', '', str(grade)))
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

# Created 2024-06-20 with ChatGPT to handle abbreviated or full text demographics_race; modified 2024-10-01
# with option to incorporate hispanic status into PEER
def set_up_demographic_flags(df, peer=True, hispanic=True, pell=True, first_generation=True, sex=True):
    """
    Sets up demographic flags in the given DataFrame based on specified demographic criteria.

    This function adds several columns to the DataFrame indicating demographic flags for:
    - PEER group membership based on race and ethnicity (Hispanic)
    - PELL grant eligibility
    - First-generation status
    - Sex

    Each of these flags is binary (1 or 0) where applicable, and the function allows for
    customization of which flags to generate.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame that contains student demographic data, including fields for
        race, Hispanic ethnicity, PELL grant eligibility, first-generation status, and sex.
    peer : bool, optional
        If True, adds a 'flag_PEER' column based on the racial and ethnic background of the student.
        PEER status is determined using a combination of race and Hispanic ethnicity (default is True).
    hispanic : bool, optional
        If True, adds a 'flag_hispanic' column based on whether the student is Hispanic (default is True).
        The 'flag_PEER' column is also influenced by this flag when it is set.
    pell : bool, optional
        If True, adds a 'flag_PELL' column indicating whether the student has received a PELL grant
        (default is True).
    first_generation : bool, optional
        If True, adds a 'flag_first_generation' column indicating whether the student is
        a first-generation college student (default is True).
    sex : bool, optional
        If True, adds a 'flag_sex' column based on the student's sex (default is True).

    Returns
    -------
    pandas.DataFrame
        The input DataFrame with additional columns for the demographic flags as specified
        by the function's parameters.

    Notes
    -----
    - The 'flag_PEER' column is determined based on racial and ethnic classifications:
      - 'American Indian or Alaska Native', 'Black or African American', and 'Hispanic'
        students are flagged as PEER (underrepresented minority).
      - Students with 'More Than One Race Reported' may also be flagged as PEER.
    - If `hispanic` is set to True, students flagged as Hispanic will automatically have `flag_PEER` set to 1
      even if their race is marked as 'Not Reported' or 'More Than One Race Reported'.
    """

    df = df.copy() # avoid changing altering the origianl dataframe

    # Mapping for full descriptions
    full_peer_dict = {
        'American Indian or Alaska Native': 1, 'Asian': 0, 'Black or African American': 1,
        'More Than One Race Reported': 2, 'Not Reported': -1, 'White': 0, 'Pacific Islander':1,
        'Native Hawaiian or Pacific Islander':1
    }

    # Mapping for abbreviated race codes
    abbrev_peer_dict = {
        'B': 'Black or African American', 'W': 'White', 'Z': 'Asian',
        'P': 'Pacific Islander', 'I': 'American Indian or Alaska Native',
        'H': 'Hispanic', 'N': 'Not Reported', 'M': 'More Than One Race Reported'
    }

    if hispanic:
        if 'demographics_hispanic' in df.columns:
            df['flag_hispanic'] = 0
            hispanic_dict = {'Non-Hispanic': 0, 'Hispanic': 1}
            df['flag_hispanic'] = df['demographics_hispanic'].map(hispanic_dict).fillna(0).astype(int)

        elif 'demographics_ethnicity' in df.columns:
            df['flag_hispanic'] = 0
            df['flag_hispanic'] = df['demographics_ethnicity'].map({1:0, 2:1}).fillna(0).astype(int)

    # Convert abbreviations to full text using mapping
    if peer:
        # Initialize flag with default value for non-matches
        df['flag_PEER'] = 0

        # Function to determine PEER status
        def determine_peer(race_str):
            # Check for direct matches in full descriptions
            if race_str in full_peer_dict:
                return full_peer_dict[race_str]

            # Handle abbreviations
            if isinstance(race_str, str):
                # Split multi-letter abbreviations and map each to the full description
                matches = [full_peer_dict[abbrev_peer_dict[letter]] for letter in race_str if
                           letter in abbrev_peer_dict]
                # Decide PEER status based on matches
                if matches:
                    return max(matches)  # Assuming more inclusive criterion for PEER status
            return 0  # Default for no matches or undefined behavior

        # Apply the function to determine PEER status
        df['flag_PEER'] = df['demographics_race'].apply(determine_peer)

        # In many cases, a student's ethnicity may be indicated as Hispanic but race was not indicative of PEER status
        # when function calls for hispanic flag to be applied, then the 'demographics_hispanic' is used to create the flag
        # and 'flag_PEER' assignment takes into account both race and ethnicity.
        if hispanic:
            df['flag_PEER'] = df.apply(
                    lambda row: 1 if row['flag_hispanic'] == 1 and row['flag_PEER'] in [0,-1, 2] else row['flag_PEER'],
                    axis=1)
    if sex:
        sex_dict = {'Female': 1, 'Male': 0, 'F': 1, 'M': 0}
        df['flag_sex'] = df['demographics_sex'].map(sex_dict).fillna(-1).astype(int)

    if first_generation:
        df['flag_first_generation'] = df['flag_first_generation'].replace({'Y': 1, 'N': 0, np.nan: 0}).astype(int)

    if pell:
        df['flag_PELL'] = df['flag_PELL'].replace({'Y': 1, 'N': 0, np.nan: 0}).astype(int)

    return df

def lookup_major_name(major):
    """
        Look up the full name of a major based on its abbreviation.

        This function takes a major abbreviation as input and returns the corresponding
        full name of the major using a predefined dictionary `majors_dict`. If the
        abbreviation is not found in the dictionary, the function returns 'Other'.
        If the input is missing (NaN), it returns NaN.

        Parameters:
        -----------
        major : str or NaN
            The abbreviation of the major (e.g., 'BIO', 'CSC', etc.).

        Returns:
        --------
        str or NaN
            The full name of the major corresponding to the abbreviation. Possible
            return values include the full names like 'Biology', 'Computer Science',
            'Psychology', 'Other', or NaN (for missing values).
    """

    # dictionary map for major abbreviations
    majors_dict = {
        'BNUR': 'Nursing',
        'BIO': 'Biology',
        'EXS': 'Exercise Science',
        'IDS': 'Interdisciplinary Studies',
        'NEUR': 'Neuroscience',
        'CHM': 'Chemistry',
        'PHY': 'Physics',
        'GEOS': 'Geosciences',
        'MTH': 'Mathematics',
        'GLY': 'Geology',
        'GEO': 'Geosciences',
        'GEOL': 'Geology',
        'GEOP': 'Geology',
        'CSC': 'Computer Science',
        'CSCI': 'Computer Science',
        'PSY': 'Psychology'
    }

    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    elif major in majors_dict:
        return majors_dict[major]
    else:
        return 'Other'


# Define function to combine spring/summer based on presence of both terms
def combine_spring_summer_terms(df, remove_original = False):
    """
    Combines spring (YYYY01) and summer (YYYY05) terms into a single term per year for each student,
    while retaining all original columns in the dataframe. New combined rows are created with
    `demographics_term` set to a unique code (`YYYY04.xx`) and appended to the dataframe without
    removing the original spring or summer rows.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe containing at least the following columns:
        - 'student_ID' : Identifier for each student.
        - 'demographics_term' : Term codes in YYYYMM integer format (e.g., 202301 for spring 2023).
        - Any additional columns representing demographic data that will be included in combined rows.

    Returns
    -------
    pandas.DataFrame
        The original dataframe with additional rows for each combined spring-summer term.
        Each new row will contain:
        - 'student_ID' : Same as in the original rows.
        - 'demographics_term' : Set to a combined code based on available terms:
            - YYYY04.11 if both spring and summer terms are present.
            - YYYY04.10 if only the spring term is present.
            - YYYY04.01 if only the summer term is present.
            - The decimal format can be interpreted as binary indicators, where the first decimal
              position represents the presence of the spring term and the second position indicates
              the summer term.
        - Other columns will contain values from either the spring or summer row based on precedence.

    Precedence Rules
    ----------------
    - If both spring (YYYY01) and summer (YYYY05) terms exist for a `student_ID` in a given year,
      the values for columns other than 'demographics_term' in the new combined row are copied from
      the summer term row (i.e., summer takes precedence).
    - If only the spring term exists, the new row's values are copied from the spring term row.
    - If only the summer term exists, the new row's values are copied from the summer term row.

    Notes
    -----
    - This function assumes that `demographics_term` is in integer format.
    - A temporary column 'year' is added and then dropped at the end to facilitate grouping by year.
    - Original rows are not modified or removed, allowing flexible filtering of combined and original terms.

    Example
    -------
    >>> df = pd.DataFrame({
    ...     'student_ID': ['AA', 'AA', 'BB', 'BB', 'BB', 'BB'],
    ...     'demographics_term': [202301, 202305, 202308, 202401, 202405, 202408],
    ...     'major_term': ['BIO', 'CHM', 'PDa', 'POT', 'FAR', 'BIO']
    ... })
    >>> df_combined = combine_spring_summer_terms(df)
    >>> print(df_combined)
    """

    df = df.copy()
    combined_rows = []

    # Extract year and create spring and summer term masks
    df['year'] = df['demographics_term'] // 100
    spring_mask = df['demographics_term'] % 100 == 1
    summer_mask = df['demographics_term'] % 100 == 5

    # Group by student and year, then determine combined term row values
    for (student_id, year), group in df.groupby(['student_ID', 'year']):
        # Check for the existence of spring and summer terms
        has_spring = spring_mask[group.index].any()
        has_summer = summer_mask[group.index].any()

        if has_spring and has_summer:
            # Combined term for both spring and summer; summer takes precedence for other values
            combined_code = year * 100 + 4.11
            combined_row = group[summer_mask[group.index]].iloc[0].copy()
            combined_row['demographics_term'] = combined_code
            combined_rows.append(combined_row)
        elif has_spring:
            # Only spring term exists
            combined_code = year * 100 + 4.10
            combined_row = group[spring_mask[group.index]].iloc[0].copy()
            combined_row['demographics_term'] = combined_code
            combined_rows.append(combined_row)
        elif has_summer:
            # Only summer term exists
            combined_code = year * 100 + 4.01
            combined_row = group[summer_mask[group.index]].iloc[0].copy()
            combined_row['demographics_term'] = combined_code
            combined_rows.append(combined_row)

    # Concatenate the combined rows as a new DataFrame and append in bulk
    combined_df = pd.DataFrame(combined_rows)
    result_df = pd.concat([df, combined_df], ignore_index=True)


    # Optional removal of original spring/summer terms
    if remove_original:
        result_df = result_df[~result_df['demographics_term'].isin(df[spring_mask | summer_mask]['demographics_term'])]

    result_df = result_df.sort_values(by=['student_ID', 'demographics_term']).reset_index(drop=True)

    # Drop the temporary 'year' column for a clean return
    result_df.drop(columns=['year'], inplace=True)

    return result_df


def classify_discipline(major):
    """
      Categorize majors into disciplines based on a predefined mapping.

      This function takes a major abbreviation as input and returns the corresponding
      discipline category. The function uses a dictionary `discipline_dict` to map
      certain major codes (e.g., 'BIO', 'BNUR') to their respective disciplines
      (e.g., 'Biology', 'STEM-Related', 'Other STEM'). If the major is not found in
      the dictionary, it categorizes the major as 'Non-STEM'. If the major is missing
      (NaN), it returns NaN.

      Parameters:
      -----------
      major : str or NaN
          The major abbreviation code to be categorized (e.g., 'BIO', 'CSC', etc.).

      Returns:
      --------
      str or NaN
          The discipline category based on the mapping. Possible return values include:
          'Biology', 'STEM-Related', 'Other STEM', 'Non-STEM', or NaN (for missing values).
      """
    discipline_dict = {
        'BNUR': 'STEM-Related',
        'BIO': 'Biology',
        'EXS': 'Other STEM',
        'IDS': 'Interdisciplinary Studies',
        'NEUR': 'Other STEM',
        'CHM': 'Other STEM',
        'PHY': 'Other STEM',
        'GEOS': 'Other STEM',
        'MTH': 'Other STEM',
        'GLY': 'Other STEM',
        'GEO': 'Other STEM',
        'GEOL': 'Other STEM',
        'GEOP': 'Other STEM',
        'CSC': 'Other STEM',
        'CSCI': 'Other STEM',
        'PSY': 'STEM-Related'
    }
    if pd.isna(major):
        return np.nan  # Return NaN for missing values
    elif major in discipline_dict:
        return discipline_dict[major]
    else:
        return 'Non-STEM'



def filter_and_calculate_crosslisted_grade_distribution(input_df=None, grade_columns=None, flag=None,
                                                        min_students_threshold=None, scramble_instructor_id = True):
    """
    Filters and calculates grade distributions for cross-listed course sections.

    Parameters:
    - input_df (pd.DataFrame): Input DataFrame with course data (required).
    - grade_columns (list): List of grade columns (e.g., ['A', 'B', 'C', 'D', 'F']). If not provided, default is used.
    - flag (str): Column name used to split subgroups (e.g., 'flag_first_generation'). If None, flag-based filtering is skipped.
    - min_students_threshold (int): Minimum number of students required in each subgroup. If None, no threshold is applied.

    Returns:
    - pd.DataFrame: DataFrame with grade distributions (proportions) for valid cross-listed sections, including the total
                    number of students for each row.

    NOTES: created by Paul Ulrich (2025-01-27; base function extended with assistance from ChatGPT4o). Note the XLIST column provided by BANNER is unreliable.
    Crosslisted combined ID should be comprised unambiguously prior to running this function, which may involve concatenation of course name, semester, day, and time
    """

    # Generate alphanumeric codes (e.g., A-Z, AA-ZZ, etc.) for instructor codes
    def generate_alphanumeric_codes(n):
        """Generate a list of alphanumeric codes to accommodate n unique values."""
        alphabet = list(string.ascii_uppercase)  # A-Z
        codes = []

        # Single letters
        codes.extend(alphabet)

        # Multi-letter combinations (AA, AB, ..., ZZ)
        i = 2

        while len(codes) < n:
            # Create combinations of `i` letters
            codes.extend([''.join(x) for x in pd.MultiIndex.from_product([alphabet] * i)])
            i += 1

        return codes[:n]


    # Validate input DataFrame
    if input_df is None or not isinstance(input_df, pd.DataFrame):
        raise TypeError("input_df is a required argument and must be a pandas DataFrame.")

    # Use default grade columns if none are provided
    if grade_columns is None:
        grade_columns = ['A', 'B', 'C', 'D', 'F']

    dataset_df = input_df.copy()

    # If flag is not provided, calculate distributions without subgrouping
    if flag is None:
        print("No flag provided. Calculating overall grade distributions for cross-listed sections.")

        # Calculate grade proportions
        proportions_df = (
            dataset_df.groupby(['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id'])[
                'course_grade_letter_simp']
            .value_counts(normalize=True)
            .unstack(fill_value=0)
            .reindex(columns=grade_columns, fill_value=0)  # Ensure all grade columns exist
            .reset_index()
        )

        # Rename grade columns for clarity (e.g., A -> pA, B -> pB)
        proportions_df.rename(columns={grade: f'p{grade}' for grade in grade_columns}, inplace=True)

        # Calculate total number of students
        total_students_df = (
            dataset_df.groupby(['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id'])[
                'course_grade_letter_simp']
            .count()
            .reset_index(name='total_students')
        )

        # Merge total student counts into proportions_df
        proportions_df = pd.merge(proportions_df, total_students_df,
                                  on=['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id'])

        # Reorder columns: total_students should come before proportions
        proportions_df = proportions_df[
            ['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', 'total_students'] +
            [f'p{grade}' for grade in grade_columns]
        ]

        # Use factorize to assign a unique numeric index to each instructor and map to instructors
        proportions_df['instructor_full_name'] = proportions_df['PROFESSOR_LAST_NAME'] + "_" + proportions_df[
            'PROFESSOR_FIRST_NAME'] # Combine last and first names to ensure uniqueness
        codes, uniques = pd.factorize(proportions_df['instructor_full_name'])
        alphanumeric_codes = generate_alphanumeric_codes(len(uniques))
        proportions_df['instructor_code'] = [alphanumeric_codes[code] for code in codes]

        if scramble_instructor_id:
            proportions_df['course_instructor_id'] = proportions_df['course_instructor_id'].apply(
                lambda x: scramble_ID(str(round(x)), cipher=os.environ['STUDENT_SUCCESS_CIPHER'])
            )

        return proportions_df

    # Count grades per cross-listed group and aggregate by flag
    counts_df = (
        dataset_df.groupby(['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag])[
            'course_grade_letter_simp']
        .value_counts()
        .unstack(fill_value=0)
    )


    # Aggregate student counts per flag
    total_students_per_flag = counts_df.sum(axis=1).unstack(fill_value=0)

    if min_students_threshold is not None:
        # Filter valid pairs where both subgroups meet the threshold
        valid_crosslisted_ids = total_students_per_flag[
            # (total_students_per_flag[0] >= min_students_threshold) &
            # (total_students_per_flag[1] >= min_students_threshold)
            # using .get() addresses situations where a course may have no one who meets one of the flag states
            (total_students_per_flag.get(0, 0) >= min_students_threshold) &
            (total_students_per_flag.get(1, 0) >= min_students_threshold)

        ].index

        #print(
        #    f"{len(valid_crosslisted_ids)} course sections taught by {valid_crosslisted_ids.get_level_values('PROFESSOR_LAST_NAME').nunique()} unique instructors have at least {min_students_threshold} in each {flag} subgroup.\n")

        # Get valid crosslisted_combined_IDs
        crosslisted_combined_IDs = valid_crosslisted_ids.get_level_values('crosslisted_combined_ID').unique()
        crosslisted_combined_IDs_list = crosslisted_combined_IDs.tolist()

        # print("Length of crosslisted_combined_IDs:", len(crosslisted_combined_IDs))
        # print("Valid crosslisted_combined_IDs extracted:", crosslisted_combined_IDs_list[:10])
        # print("Unique count:", len(crosslisted_combined_IDs_list))

        # Filter dataset to valid cross-listed sections
        filtered_dataset_df = dataset_df[dataset_df['crosslisted_combined_ID'].isin(crosslisted_combined_IDs_list)]
        # print(f"There are {filtered_dataset_df['crosslisted_combined_ID'].nunique()} sections in filtered_dataset_df.")
    else:
        # If no minimum threshold, use the full dataset
        print("No minimum student threshold provided. Using all cross-listed sections for analysis.")
        filtered_dataset_df = dataset_df

    # Calculate grade proportions for valid cross-listed sections
    proportions_df = (
        filtered_dataset_df.groupby(['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag])[
            'course_grade_letter_simp']
        .value_counts(normalize=True)
        .unstack(fill_value=0)
        .reindex(columns=grade_columns, fill_value=0)  # Ensure all grade columns exist
        .reset_index()
    )

    # Add clarity to column names
    proportions_df.columns = (['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag] +
                              [f'p{grade}' for grade in grade_columns]
                              )

    # Add total student counts
    total_counts_df = (
        filtered_dataset_df.groupby(['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag])[
            'course_grade_letter_simp']
        .count()
        .reset_index(name='total_students')
    )

    # Merge total student counts into proportions_df
    proportions_df = pd.merge(proportions_df, total_counts_df, on=['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag])
    proportions_df = proportions_df[
        ['course_term', 'crosslisted_combined_ID', 'PROFESSOR_LAST_NAME', 'PROFESSOR_FIRST_NAME', 'course_instructor_id', flag, 'total_students'] +
        [f'p{grade}' for grade in grade_columns]
        ]

    # Use factorize to assign a unique numeric index to each instructor and map to instructors
    proportions_df['instructor_full_name'] = proportions_df['PROFESSOR_LAST_NAME'] + "_" + proportions_df[
        'PROFESSOR_FIRST_NAME']  # Combine last and first names to ensure uniqueness
    codes, uniques = pd.factorize(proportions_df['instructor_full_name'])
    alphanumeric_codes = generate_alphanumeric_codes(len(uniques))
    proportions_df['instructor_code'] = [alphanumeric_codes[code] for code in codes]

    if scramble_instructor_id:
        proportions_df['course_instructor_id'] = proportions_df['course_instructor_id'].apply(
            lambda x: scramble_ID(str(round(x)), cipher=os.environ['STUDENT_SUCCESS_CIPHER'])
        )

    return proportions_df
