# Let's write a helper function to adjust the graduation term to the end of the term
import pandas as pd
from tkinter import filedialog as fd
import tkinter as tk
import re

#[Utility function] permit simple ciphering of Student_ID numbers; depending on input, returns either a dataframe or a string
#working_df : dataframe where Student_ID is the column to be ciphered
#cipher : a string of characters length of Student_ID; DON'T FORGET THIS AND DO NOT POST PUBLICALLY
def scramble_ID(input_data, cipher):
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
            if 'Student_ID' not in results_df.columns:
                print("The dataframe does not have a 'Student_ID' column.")
                return None

            # Scramble IDs for a dataframe
            results_df["Student_ID"] = (
                results_df["Student_ID"]
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
            print("Input must be a pandas DataFrame or a string representing a Student_ID.")
            return None

#[Utility function] accepts a single, scrambled Student_ID and unscrambles it (given the appropriate cipher string)
#Student_ID : string of characters representing the Student_ID to be unscrambled
#cipher : a string of characters length of Student_ID; DON'T FORGET THIS AND DO NOT POST PUBLICALLY
def unscramble_ID(Student_ID, cipher):
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
    original_id = ''.join([unscrambleDict[char] for char in Student_ID])

    return original_id

#[Utility function]  adjust grad_term to give the ending month from a beginning of a grad_term 2023-07-12
def adjust_grad_term(row):
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
    df_copy['Final_GRDE_Simp'] = df_copy['Final_GRDE'].apply(lambda grade: re.sub(r'[%\^R#@*+-]', '', str(grade)))
    df_copy['Final_GRDE_Simp'] = df_copy['Final_GRDE_Simp'].map(grade_mapping).fillna(df_copy['Final_GRDE_Simp'])

    return df_copy

#Utility function: gets user input on which CSV grades reports files to load and returns as a pandas dataframe
def load_grades():
    csv_filename = fd.askopenfilename(title = 'Please select the grades file') # show an "Open" dialog box and return the path to the selected file
    print(csv_filename)
    grades_df = pd.read_csv(csv_filename)
    return grades_df

#[Utility function] accepts demographic dataframe and returns dataframe for first semester demographics
#of students based on presence/absence of transfer credits. This is a rough approximation of first time, first year
#Since SDSTUMAIN_MATRIC_TERM is not always exactly matched to the first term a student takes courses, the dataframe
#is sorted to find the first demographics term for each student.
#df: dataframe with demographics data
#transfer: 0 = get all students (default); 1 = get students with transfer credits; 2 = get students with no transfer credits
#return_dataframe: Boolean; 1 = return results as entire dataframe; 0 = return results as a list of unique student ID's
def demographics_first_semester(df, transfer = 0, return_dataframe = 1):
    # Get the earliest term for each student
    mask = df.groupby('Student_ID')['SDSTUDEMOG_TERM'].idxmin()
    earliest_df = df.loc[mask]

    # return dataframe containing first semester demographics for ALL students
    if (transfer == 0):
        if return_dataframe == 1:
            return earliest_df
        elif return_dataframe == 0:
            return list(earliest_df['Student_ID'])

    # return dataframe containing first semester demographics for students who WITH transfer credit
    elif (transfer == 1):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['SDSTUMAIN_TRANSFER_HOURS'] > 0) & (~earliest_df['SDSTUMAIN_TRANSFER_HOURS'].isna())]
        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['Student_ID'])

    # return dataframe containing first semester demographics for students WITHOUT transfer credit
    elif (transfer == 2):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['SDSTUMAIN_TRANSFER_HOURS'].isna()) | (earliest_df['SDSTUMAIN_TRANSFER_HOURS'] == 0)]

        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['Student_ID'])


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