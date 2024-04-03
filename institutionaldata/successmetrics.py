import pandas
import pandas as pd
import numpy as np

import institutionaldata.utilityfunctions
import institutionaldata.utilityfunctions as utilityfunctions
import matplotlib.pyplot as plt
from tabulate import tabulate
from tkinter import filedialog as fd
import tkinter as tk
import datetime
import pydot
import pygraphviz as pgv
import statsmodels.api as sm
from matplotlib.backends.backend_pdf import PdfPages

#Determine the number of students who were retained in a major since the semester of matriculation
#major_code : 'BIO', 'CHM', etc
#years : four digit calendar year such as 2024
#ftfy : "first time first year" argument; when True, only those students with 0 transfer credits will be in the output
#2023-07-12 developed using ChatGPT 4.0 with Code Interpreter
# def major_retention_v1(student_df, major_code, years, ftfy = True):
#     semester_codes = utilityfunctions.create_semesters(years)
#     print(semester_codes)
#
#     # Import the dataset
#     working_df = student_df.copy()
#     #working_df['Grad_term'] = working_df['Grad_term'].apply(utilityfunctions.adjust_grad_term)
#     #semesters = list()
#
#     #First time, first year argument ftfy defaults to True to in function. However, if we want to catch all students who matriculated in a time frame, the dataframe must not drop those with transfer credit
#     if ftfy == False:
#         working_df = working_df[
#             (working_df['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
#             (working_df['SDSTUMAIN_MAJOR'] == major_code) &
#             (working_df['SDSTUMAIN_MATRIC_TERM'] == working_df['SDSTUDEMOG_TERM'])
#             ]
#         print(working_df)
#
#     #If only FTFY students are desired (default behavior), dataframe should have 0 transfer hours
#     else:
#         working_df = working_df[
#             (working_df['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
#             (working_df['SDSTUMAIN_MAJOR'] == major_code) &
#             (working_df['SDSTUMAIN_MATRIC_TERM'] == working_df['SDSTUDEMOG_TERM']) &
#             (working_df['SDSTUMAIN_TRANSFER_HOURS'].isna() | (
#                     working_df['SDSTUMAIN_TRANSFER_HOURS'] == 0))
#             ]
#         print(working_df)
#
#
#     # Compute the new column
#     working_df['SDSTUMAIN_MATRIC_TERM'] = pd.to_datetime(working_df['SDSTUMAIN_MATRIC_TERM'], format='%Y%m')
#     working_df['Grad_term'] = pd.to_datetime(working_df['Grad_term'], format='%Y%m')
#     working_df['Grad_term_end'] = working_df['Grad_term'].apply(utilityfunctions.adjust_grad_term)
#     working_df['Months_Between'] = (working_df['Grad_term_end'].dt.year - working_df[
#         'SDSTUMAIN_MATRIC_TERM'].dt.year) * 12 + working_df['Grad_term_end'].dt.month - working_df[
#                                        'SDSTUMAIN_MATRIC_TERM'].dt.month
#
#     #Provide boolean flag to simplify various measures
#     working_df['grad_flag'] = working_df['Grad_term'].notnull().astype(int)
#     major_retention_flag = 'major_retention' + major_code
#     working_df[major_retention_flag] = 0
#     working_df.loc[(working_df['Grad_term'].notnull()) & (working_df['Major'] == major_code), major_retention_flag] = 1
#     # Compute the summary statistics
#     total_students = working_df.shape[0]
#     non_graduates = working_df['Grad_term'].isna().sum()
#     graduates = total_students - non_graduates
#     major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)].shape[0]
#     non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)].shape[0]
#
#
#     #Compute time till graduation for different segments
#     average_months_all = working_df['Months_Between'].mean()
#     std_dev_months_all = working_df['Months_Between'].std()
#     average_years_non_graduates = working_df[working_df['Grad_term'].isna()]['Months_Between'].mean()/12  # Should be NaN
#     std_dev_years_non_graduates = working_df[working_df['Grad_term'].isna()]['Months_Between'].std()/12  # Should be NaN
#     average_years_graduates = working_df[working_df['Grad_term'].notna()]['Months_Between'].mean()/12
#     std_dev_years_graduates = working_df[working_df['Grad_term'].notna()]['Months_Between'].std()/12
#
#     average_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)]['Months_Between'].mean() / 12
#     std_dev_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)][
#         'Months_Between'].std()/12
#
#     average_years_non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)][
#                                       'Months_Between'].mean() / 12
#     std_dev_years_non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)][
#                                       'Months_Between'].std() / 12
#
#     #Compute institutional GPA at graduation for graduates in the specific major or different major
#
#     #average_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)]['Months_Between'].mean() / 12
#     #std_dev_years_bio_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == 'BIO')][
#     #                                  'Months_Between'].std() / 12
#
#     #Need to pull in demog data from demographics of last semester because graduation purge report does not include GPA
#     #gpa_all_graduates = working_df[(working_df['Grad_term'].notna())[]
#     #gpa_bio_graduates =
#     #gpa_non_bio_graduates
#
#     # Create the summary DataFrame
#     summary_df = pd.DataFrame(
#         columns=['Category', 'Count', 'Percentage', 'Avg Years to Graduation', 'Std Dev Years to Graduation'])
#
#     rows_list = [
#         {'Category': 'Total Students', 'Count': total_students, 'Percentage': 100, 'Avg Years to Graduation': None,
#          'Std Dev Years to Graduation': None},
#         {'Category': 'Non-Graduates', 'Count': non_graduates, 'Percentage': non_graduates / total_students * 100,
#          'Avg Years to Graduation': average_years_non_graduates,
#          'Std Dev Years to Graduation': std_dev_years_non_graduates},
#         {'Category': 'Graduates', 'Count': graduates, 'Percentage': graduates / total_students * 100,
#          'Avg Years to Graduation': average_years_graduates, 'Std Dev Years to Graduation': std_dev_years_graduates},
#         {'Category': 'Graduates Retained within Major', 'Count': major_code_graduates, 'Percentage': major_code_graduates / total_students * 100,
#          'Avg Years to Graduation': average_years_major_code_graduates,
#          'Std Dev Years to Graduation': std_dev_years_major_code_graduates},
#         {'Category': 'Graduates who Left Major', 'Count': graduates - major_code_graduates,
#          'Percentage': (graduates - major_code_graduates) / total_students * 100,
#          'Avg Years to Graduation': average_years_non_major_code_graduates,
#          'Std Dev Years to Graduation': std_dev_years_non_major_code_graduates}
#     ]
#
#     summary_df = pd.concat([summary_df, pd.DataFrame(rows_list)], ignore_index=True)
#
#     # Return the result
#     return(summary_df, working_df)

#Calculate the number of math courses taken by a subset of students
#major code: major (e.g. 'BIO', 'CHM', 'PSY')
#ftfy : "first time first year" argument; when True, only those students with 0 transfer credits will be in the output
#grade_options: a list of the letter grades for which you want specifics such as 'D', 'F', or 'W'; NOTE: this needs to be ironed out more (20230724, PNU)
#math_grades_df: Pandas dataframe including the grades; default is None; if no dataframe is provided as argument, user prompted with dialog to select file
def num_math_courses(demographics_df, major_code, years, math_grades_df = None, ftfy = True, grade_options = None):
    # Load the math course grades
    if math_grades_df is None:
        root = tk.Tk()
        root.withdraw()
        file_path = fd.askopenfilename(filetypes=[('Select the CSV file containing the grades you want to analyze', '*.csv')])
        print(file_path)
        math_grades_df = pd.read_csv(file_path)

    # Create copies of these dataframes for downstream analysis and create list of semester codes based on years argument
    math_grades_df_copy = math_grades_df.copy(deep=True)
    demographics_df_copy = demographics_df.copy(deep=True)
    semester_codes = utilityfunctions.create_semesters(years)

    #Eliminate duplicate rows of data
    math_grades_df_copy.drop_duplicates(subset=['Student_ID', 'Reg_Crn', 'Reg_Term', 'Final_GRDE'], keep="first",
                                             inplace=True)
    math_grades_df_copy['Final_GRDE_Simp'] = utilityfunctions.letter_grade_simplify(math_grades_df_copy, c_minus_flag= 1)['Final_GRDE_Simp']

    #Use the ftfy flag to include or exclude student with transfer credits; default is ftfy = True to exclude
    if ftfy == False:
        major_code_df = demographics_df_copy[
            (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
            (demographics_df_copy['SDSTUMAIN_MAJOR'] == major_code) &
            (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'] == demographics_df_copy['SDSTUDEMOG_TERM'])]

    else:
         # Adjust the filtering to include only rows where 'SDSTUMAIN_TRANSFER_HOURS' is 0 or NaN
         major_code_df = demographics_df_copy[
             (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
             (demographics_df_copy['SDSTUMAIN_MAJOR'] == major_code) &
             (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'] == demographics_df_copy['SDSTUDEMOG_TERM']) &
             (demographics_df_copy['SDSTUMAIN_TRANSFER_HOURS'].isna() | (
                         demographics_df_copy['SDSTUMAIN_TRANSFER_HOURS'] == 0))
             ]

    # Get the list of students who matriculated as these majors and filter math_grade_df_copy for these students
    major_code_student_ids = major_code_df['Student_ID'].unique()
    major_code_students_math_courses = math_grades_df_copy[
        math_grades_df_copy['Student_ID'].isin(major_code_student_ids)
    ]

    # Calculate the number of math courses each student took
    num_courses_per_major_code_student = major_code_students_math_courses['Student_ID'].value_counts()

    # Calculate the average number +/- standard deviation of math courses taken by these students
    avg_num_courses_per_major_code_student = num_courses_per_major_code_student.mean()
    std_dev_num_courses_per_major_code_student = num_courses_per_major_code_student.std()

    # Get the most frequently taken courses
    most_frequent_courses = major_code_students_math_courses['Reg_Crse_Title'].value_counts()

    # Calculate the mean numerical grade and withdrawal count for each of the most frequent courses
    results = []
    for course_id, count in most_frequent_courses.items():
        course_students = major_code_students_math_courses[major_code_students_math_courses['Reg_Crse_Title'] == course_id]
        num_students = len(course_students['Student_ID'].unique())

        #figure out how many of these students have graduated or did not graduate
        students_graduated = demographics_df_copy[
            (demographics_df_copy['Student_ID'].isin(course_students['Student_ID'])) &
            (~demographics_df_copy['Grad_term'].isna())
            ]

        course_students_graduated = course_students[
            course_students['Student_ID'].isin(students_graduated['Student_ID'])
        ]

        course_students_non_graduated = course_students[
            ~course_students['Student_ID'].isin(students_graduated['Student_ID'])
        ]

        num_students_graduated = len(course_students_graduated['Student_ID'].unique())
        num_students_non_graduated = len(course_students_non_graduated['Student_ID'].unique())

        avg_num_times_taken_total = count / num_students
        avg_num_times_taken_graduated = len(course_students_graduated) / num_students_graduated if num_students_graduated != 0 else 0
        #print(len(course_students_graduated), num_students_graduated)
        avg_num_times_taken_non_graduated = len(course_students_non_graduated) / num_students_non_graduated if num_students_non_graduated != 0 else 0
        #print(len(course_students_non_graduated), num_students_non_graduated)

        course_grades = course_students['Final_GRDE']
        course_grades_simplified = course_students['Final_GRDE_Simp']

        numerical_grades = course_grades.apply(utilityfunctions.num_grade_institutional)
        valid_numerical_grades = numerical_grades[numerical_grades != -1]
        mean_grade = valid_numerical_grades.mean()
        grade_std = valid_numerical_grades.std()

        withdrawals = course_grades_simplified[course_grades_simplified == 'W']
        withdrawal_count = len(withdrawals)
        df_count =  len(course_grades_simplified[(course_grades_simplified == 'D') | (course_grades_simplified == 'F')])

        grade_options_counts = {}
        if grade_options is not None:
            for grade_option in grade_options:
                course_students_with_grade_option = course_students[course_students['Final_GRDE'] == grade_option]
                num_students_with_grade_option = len(course_students_with_grade_option['Student_ID'].unique())
                avg_num_times_taken_grade_option = len(
                    course_students_with_grade_option) / num_students_with_grade_option if num_students_with_grade_option != 0 else 0
                grade_options_counts[grade_option] = avg_num_times_taken_grade_option

        #add the information for each course to the results list
        results.append({
                'Course': course_id,
                'Count': count,
                'Mean Grade': mean_grade,
                'SD': grade_std,
                'Withdrawals': withdrawal_count,
                'DF Count' : df_count,
                'Number of Unique Students': num_students,
                'Avg. Times Taken (Graduated)': avg_num_times_taken_graduated,
                'Avg. Times Taken (Non-Graduated)': avg_num_times_taken_non_graduated,
                'Number of Unique Students who Graduated': num_students_graduated,
                'Num Students Non-Graduated': num_students_non_graduated,
                **(grade_options_counts if grade_options is not None else {})

            })

    # Create a new DataFrame from results
    results_df = pd.DataFrame(results)
    print(tabulate(results_df, headers='keys', tablefmt='psql'))
    return avg_num_courses_per_major_code_student, std_dev_num_courses_per_major_code_student, results_df

#Calculate the amount of time between matriculation and taking a math course for the FIRST time
#course: course title as string
#years: year in YYYY format (e.g. 2024)
#major_code: major at matriculation
def time_before_math_course(demographics_df, course, years, ftfy = True, major_code = None, math_grades_df = None):
    # Load the math course grades if no data frame of grades provided
    if math_grades_df is None:
        root = tk.Tk()
        root.withdraw()
        file_path = fd.askopenfilename(
            filetypes=[('Select the CSV file containing the grades you want to analyze', '*.csv')])
        print(file_path)
        math_grades_df = pd.read_csv(file_path, index_col=0) #use of index_col = 0 avoids introduction of an "Unnamed 0" column that read_csv includes

    # Create copies of these dataframes for downstream analysis
    math_grades_df_copy = math_grades_df.copy(deep=True)
    demographics_df_copy = demographics_df.copy(deep=True)
    combined_df = pd.DataFrame()

    for year in years:
        semester_codes = utilityfunctions.create_semesters([year])
        #print(semester_codes)

        # Get demographics for the matriculation semester of students in specified major
        # Use the ftfy flag to include or exclude student with transfer credits; default is ftfy = True to exclude
        if ftfy == False:
            major_code_students_df = demographics_df_copy[
                (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
                (demographics_df_copy['SDSTUMAIN_MAJOR'] == major_code) &
                (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'] == demographics_df_copy['SDSTUDEMOG_TERM'])]

        else:
            # Adjust the filtering to include only rows where 'SDSTUMAIN_TRANSFER_HOURS' is 0 or NaN
            major_code_students_df = demographics_df_copy[
                (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
                (demographics_df_copy['SDSTUMAIN_MAJOR'] == major_code) &
                (demographics_df_copy['SDSTUMAIN_MATRIC_TERM'] == demographics_df_copy['SDSTUDEMOG_TERM']) &
                (demographics_df_copy['SDSTUMAIN_TRANSFER_HOURS'].isna() | (
                        demographics_df_copy['SDSTUMAIN_TRANSFER_HOURS'] == 0))
                ]

        # Get the list of students in specified major who matriculated during the semesters of this year
        major_code_student_ids = major_code_students_df['Student_ID'].unique()

        # Get all math grades associated with students who matriculated years provided in the year argument
        major_code_students_math_courses = math_grades_df_copy[
            math_grades_df_copy['Student_ID'].isin(major_code_student_ids)
        ]

        #these are the students who took the course of interest and matriculated in semesters associated with year variable
        major_code_students_course = major_code_students_math_courses[major_code_students_math_courses['Reg_Crse_Title'] == course]
        #major_code_students_course['Reg_Term'] = pd.to_datetime(major_code_students_course['Reg_Term'], format='%Y%m')
        major_code_students_course.loc[:, 'Reg_Term'] = pd.to_datetime(major_code_students_course['Reg_Term'],
                                                                       format='%Y%m')
        #get the data for the first time a student took the course of interest
        mask = major_code_students_course.groupby('Student_ID')['Reg_Term'].idxmin()
        major_code_students_course_earliest = major_code_students_course.loc[mask]

        #get all demographics associated with these students and winnow demographics down to get only one row, because I want to easily extract matriculation term
        filtered_demographics_df = demographics_df[(demographics_df['Student_ID'].isin(major_code_students_course['Student_ID'].unique())) & (demographics_df['SDSTUDEMOG_TERM'] == demographics_df['SDSTUMAIN_MATRIC_TERM'])]
        filtered_demographics_df = filtered_demographics_df[['Student_ID', 'SDSTUMAIN_MATRIC_TERM', 'SDSTUMAIN_MAJOR']]

        filtered_demographics_df['SDSTUMAIN_MATRIC_TERM'] = pd.to_datetime(filtered_demographics_df['SDSTUMAIN_MATRIC_TERM'], format='%Y%m')
        filtered_demographics_df.rename(columns={'SDSTUMAIN_MAJOR': 'Major_at_Matriculation'}, inplace=True)
        current_df = pd.merge(major_code_students_course_earliest, filtered_demographics_df, left_on='Student_ID', right_on='Student_ID', how='left')
        current_df['Years Between'] = (current_df['Reg_Term'].dt.year - current_df['SDSTUMAIN_MATRIC_TERM'].dt.year) + current_df['Reg_Term'].dt.month / 12 - current_df['SDSTUMAIN_MATRIC_TERM'].dt.month /12
        current_df.drop('Student_ID', axis=1, inplace=True)

        combined_df = pd.concat([combined_df, current_df], ignore_index=True)

        #drop anomalously duplicated rows
        combined_df.drop_duplicates(subset=['Student_ID', 'Reg_Crn', 'Reg_Term', 'Final_GRDE'], keep="first",inplace=True)
    return combined_df


def plot_grades(grades_df, letterGrades = False, title = 'Frequency Diagram of Grades'):
    #if letterGrades:
        # Define the custom bins
        custom_bins = ['A', 'B', 'C', 'D', 'F', 'W']
        # Convert the Final_GRDE_Simplified column to categorical data with custom ordering

        # Drop rows with '#NAME?' values in the Final_GRDE column
        grades_df = grades_df[grades_df['Final_GRDE'] != '#NAME?']

        #simplify letter grades
        grades_df['Final_GRDE_Simplified'] = utilityfunctions.letter_grade_simplify(grades_df['Final_GRDE'], c_minus_flag=1)

        #drop rows where the grade bin was not matched to the custom bins above. This occurs rarely, it seems (only 2 students of precalc 2011-2015 matriculants)
        grades_df = grades_df[grades_df['grade_bins'] != -1]

        grades_df['grade_bins'] = pd.Categorical(grades_df['Final_GRDE_Simplified'], categories=custom_bins, ordered=True)
        grades_df['grade_bins'] = grades_df['grade_bins'].cat.codes

        # Create the histogram using the 'grade_bins' column and the defined bins
        plt.hist(grades_df['grade_bins'], bins=len(custom_bins), edgecolor='black')
        plt.xticks(range(len(custom_bins)), custom_bins)  # Set the x-axis labels
        plt.ylabel('Frequency')  # Set the y-axis label
        plt.title(title)  # Set the title of the plot
        plt.show()

    # else:
    #     custom_bins = [-1.1, -0.001, 1, 1.669, 2.669, 3.669, 4.334]
    #     custom_bins.sort()
    #
    #     # Convert the 'NumGrade' column to categorical data with custom bins
    #     grades_df['grade_bins'] = pd.cut(grades_df['NumGrade'], bins=custom_bins, right=False, labels=False)
    #
    #     # Get the unique categories from the 'grade_bins' column
    #     categories = grades_df['grade_bins'].unique().tolist()
    #
    #     # Create the histogram using the 'grade_bins' column and the number of categories
    #     plt.hist(grades_df['grade_bins'], bins= custom_bins, edgecolor='black')
    #
    #     plt.xticks(custom_bins, custom_bins)  # Set the x-axis labels
    #     plt.xlim(custom_bins[0], custom_bins[-1])  # Set the x-axis limits
    #     plt.ylabel('Frequency')  # Set the y-axis label
    #     plt.title(title)  # Set the title of the plot
    #     plt.show()

        # # Create the histogram using the 'New_Column' and the defined bins
        # plt.hist(grades_df['NumGrade'], bins=custom_bins, edgecolor='black')
        # plt.xticks(custom_bins)  # Set the x-axis labels
        # plt.ylabel('Frequency')  # Set the y-axis label
        # plt.title(title)  # Set the title of the plot
        # plt.show()


#2023-08-23 student_ids should be a list of all student ID numbers analyzed for retention
#this can be created via list(df['Student_ID'].unique()) for all students, or a list of the students who matriculated
#with 0 transfer credits ('ftfy' students) can be generated by using the utilityfunctions.ftfy() convenience function
#as follows: institutionaldata.utilityfunctions.ftfy(df)
def major_retention(demographics_df, years, major_code, student_ids):
    #running sum of the number of academic years in which a student has been retained in the major
    def calculate_running_retention_flag(group):
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


def course_performance(course_list, major_code_list, years, demographics_df):
    #load the grade files
    root = tk.Tk()
    root.withdraw()
    file_path = fd.askopenfilename(
        filetypes=[('Select the CSV file containing the grades you want to analyze', '*.csv')])
    print(file_path)
    math_grades_df = pd.read_csv(file_path,
                                 index_col=0)  # use of index_col = 0 avoids introduction of an "Unnamed 0" column that read_csv includes

    testresults_list = []

    for course_input in course_list:
        for major_code_input in major_code_list:
            testresults = institutionaldata.successmetrics.time_before_math_course(
                demographics_df, course=course_input, math_grades_df=math_grades_df, major_code=major_code_input,
                years=years, ftfy=True)

            testresults['Num_GRDE'] = testresults['Final_GRDE'].apply(
                institutionaldata.utilityfunctions.num_grade_institutional)
            filtered_testresults = testresults[testresults['Num_GRDE'] != -1]

            bins = [0, 1, 2, 3, float('inf')]
            labels = ['<0-1', '>1-2', '>2-3', '>3']

            filtered_testresults = filtered_testresults.copy()
            filtered_testresults['Years_Between_Binned'] = pd.cut(filtered_testresults['Years Between'], bins=bins,
                                                                  labels=labels)
            testresults_list.append(filtered_testresults)

    combined_filtered_results = pd.concat(testresults_list)

    #get demographics associated with the first term of demographics (should be the same semester the student matriculated)
    sorted_df = demographics_df[
        demographics_df['Student_ID'].isin(combined_filtered_results['Student_ID'].unique())].sort_values(
        by='SDSTUDEMOG_TERM')
    result = sorted_df.drop_duplicates(subset='Student_ID', keep='first')

    #create a flag for graduation (1 = graduated, 0 = not graduated)
    result = result.copy() #using .copy() avoids wraning "a value is trying to be set on a copy of a slice from a DataFrame"
    result.loc[:, 'grad_flag'] = result['Grad_term'].notnull().astype(int)

    #select the desired columns from the dataset and derive additional columns
    new_result = result[
        ['Student_ID', 'SDSTUDEMOG_SEX', 'SDSTUDEMOG_TERM', 'SDSTUMAIN_MATRIC_TERM', 'Major', 'BirthYear', 'grad_flag']].copy()
    new_result['matriculation_year'] = new_result['SDSTUMAIN_MATRIC_TERM'].apply(lambda x: str(int(x))[:4])
    new_result['age_at_matriculation'] = new_result['matriculation_year'].astype(int) - new_result['BirthYear'].astype(
        int)

    #merge the information
    filtered_testresults = pd.merge(
        left=combined_filtered_results,
        right=new_result[['Student_ID', 'age_at_matriculation', 'SDSTUDEMOG_SEX', 'grad_flag', 'Major']],
        on='Student_ID', how='left'
    )

    return filtered_testresults

#2023-10-18 (PNU) combines math grades with demographics and returns these as a dataframe with data on first and second attempts of courses
#2023-11-09 (PNU) updated to accept first_semester_demographics_df output from utilityfunctions.demographics_first_semester()
def combine_course_grades_with_demographics(input_demographics_df):
    root = tk.Tk()
    root.withdraw()
    file_path = fd.askopenfilename(
        filetypes=[('Select the CSV file containing the grades you want to analyze', '*.csv')])
    print(file_path)
    math_grades_df = pd.read_csv(file_path)

    # eliminate fully duplicated rows in math_grades_df
    print(len(math_grades_df))
    math_grades_df = math_grades_df.drop_duplicates()
    print(len(math_grades_df))

    input_demographics_df['Grad_date'] = pd.to_datetime(input_demographics_df['Grad_date'], format='%m/%d/%Y')

    merged_df = math_grades_df.merge(input_demographics_df, left_on='Student_ID', right_on='Student_ID', how='left')


    print(list(merged_df))
    # Select only the columns you are interested in
    final_columns = [
        'Reg_Term', 'Course_Dept', 'Instr_Name', 'Reg_Crn', 'Reg_Crse_Title',
        'Student_ID', 'Final_GRDE', 'StuMajr_Code1', 'SDSTUDEMOG_SEX', 'SDSTUMAIN_MATRIC_TERM', 'Major', 'Grad_year'
    ]
    final_df = merged_df[final_columns]
    # Count the occurrences of each Student_ID in both DataFrames
    math_grades_counts = math_grades_df['Student_ID'].value_counts()
    final_df_counts = final_df['Student_ID'].value_counts()

    # Find the Student_IDs that occur more times in final_df than in math_grades_df
    common_student_ids = math_grades_counts.index.intersection(final_df_counts.index)
    duplicated_student_ids = [student_id for student_id in common_student_ids if
                              final_df_counts[student_id] > math_grades_counts[student_id]]

    #print("Duplicated Student_IDs:", duplicated_student_ids)

    columns_to_keep = ['Reg_Crse_Title', 'Instr_Name', 'Reg_Term', 'Student_ID', 'Final_GRDE', 'StuMajr_Code1',
                       'SDSTUDEMOG_TERM', 'SDSTUDEMOG_SEX', 'SDSTUMAIN_MATRIC_TERM', 'Major', 'Grad_term']
    merged_df_clean = merged_df[columns_to_keep]
    merged_df_clean = merged_df_clean.sort_values(by=['Student_ID', 'Reg_Term'])
    merged_df_clean = institutionaldata.utilityfunctions.letter_grade_simplify(merged_df_clean, c_minus_flag=1)
    first_attempts = merged_df_clean.drop_duplicates(subset=['Student_ID', 'Reg_Crse_Title'], keep='first')
    #print("# of first attempts: ", len(first_attempts))  # 31033
    first_attempts_DFW = first_attempts[first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])]  # 7579
    remaining_attempts = merged_df_clean.drop(first_attempts.index)
    second_attempts = remaining_attempts[remaining_attempts['Student_ID'].isin(first_attempts_DFW['Student_ID'])]
    second_attempts = second_attempts.drop_duplicates(subset=['Student_ID', 'Reg_Crse_Title'], keep='first')  # 3515
    combined_attempts = pd.concat([first_attempts, second_attempts])

    return combined_attempts

#2023-10-27 Modified base code with ChatGPT4.0 to create subsequent course analysis work
#2024-01-19 Revised and improved calculations because proportions of retakes were incorrect; used lots print statements to follow calculations
#2024-02-21 Ironed out inconsistencies in numbers that occurred due to inaccurate filtering, counting, and anomalous student scenarios
def analyze_course(course_name, df, major_matriculation, prerequisite_course = False, node_pie = False):
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

    Notes
    -----
    This function analyzes student performance and attempt statistics for a given course. It filters the input DataFrame
    to include only attempts for the specified course, then calculates descriptive statistics for first attempts, including
    pass rates and DFW rates. If second attempts exist, it further analyzes the performance on those attempts.

    Example
    -------
    To analyze the performance statistics for a course named 'CHEM101' for students majoring in 'Chemistry', you can use:
    analyze_course(course_name = 'Principles of Chemistry I', df, major_matriculation = 'CHM')
    """


    # Check if DataFrame is empty
    if df.empty:
        print("DataFrame is empty.")
        return None

    # Step 1: Get all attempts for the course
    course_df_all_attempts = df[(df['course_title'] == course_name)]  # the reason we don't filter by major yet is because students in major at first attempt may switch to another major later
    course_df_all_attempts = course_df_all_attempts.sort_values(by=['student_ID', 'course_term'], ascending=[True, True])
    #print(f"Total attempts for {course_name}: {len(course_df_all_attempts)}")

    # Check if there are no attempts for the course
    if course_df_all_attempts.empty:
        print(f"No attempts found for {course_name}.")
        return None

    course_df_first_attempts_all = course_df_all_attempts.drop_duplicates(subset=['student_ID'], keep='first')
    #print(f"Number of unique students in first attempt of {course_name}: {len(course_df_first_attempts_all)}")

    # Step 2: Identify students with desired major in first attempt
    desired_major_students = course_df_first_attempts_all[(course_df_first_attempts_all['major_matriculation'] == major_matriculation)]['student_ID'].unique()


    #print(f"Number of unique {major_matriculation} majors  : {len(desired_major_students)}")

    # Step 3: Filter all attempts for these students
    course_df = course_df_all_attempts[course_df_all_attempts['student_ID'].isin(desired_major_students)]
    course_df_first_attempts = course_df.drop_duplicates(subset=['student_ID'], keep='first')

    # Descriptives for the first attempts
    first_pass_number = len(course_df_first_attempts[course_df_first_attempts['course_grade_letter_simp'].isin(['A', 'B', 'C'])])
    #print(f"First pass number : {first_pass_number}")

    first_pass_proportion = first_pass_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0
    first_DFW_number = len(course_df_first_attempts[course_df_first_attempts['course_grade_letter_simp'].isin(['D', 'F', 'W'])])
    #print(f"First DFW number : {first_DFW_number}")
    first_DFW_proportion = first_DFW_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0

    # Repeat analysis for students who did not pass the first time
    course_df_repeat_attempts_all = course_df[course_df.duplicated(subset=['student_ID'], keep=False)]
    #print("Number of all repeats who did not pass the first time : ", len(course_df_repeat_attempts_all))
    #print("Number of all unique students who did not pass the first time :", len(course_df_repeat_attempts_all['student_ID'].unique()))
    course_df_second_attempts = course_df_repeat_attempts_all[course_df_repeat_attempts_all.duplicated(subset=['student_ID'], keep='first')]

    print("Current course is:", course_name)
    # Step 2: Filter to include only those students who attempted the course more than once for the second attempt analysis
    grouped_second_attempters_df = course_df_all_attempts[course_df_all_attempts['major_matriculation'] == major_matriculation].groupby('student_ID').filter(lambda x: len(x) > 1)
    #grouped_second_attempters_df = filtered_df.groupby('Student_ID').filter(lambda x: len(x) > 1)
    # Step 3: Filter to include only the rows corresponding to the second attempt
    first_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(0)
    second_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(1)
    #print(len(course_df_first_attempts['student_ID'].unique()))
    proportion_DFW_repeat = len(second_attempt_df) / first_DFW_number if first_DFW_number > 0 else 0
    #print(proportion_DFW_repeat)
    # Step 4: Count the number of students who passed and failed in their second attempts
    # proportion_DFW_repeat = len(second_attempt_df) / first_DFW_number if first_DFW_number > 0 else 0
    second_attempt_number = len(second_attempt_df)
    #print(len(course_df_second_attempts))
    second_pass_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['A', 'B', 'C'])][
        'student_ID'].nunique()
    second_pass_proportion = second_pass_number / len(grouped_second_attempters_df['student_ID'].unique()) if len(
        grouped_second_attempters_df) > 0 else 0

    second_DFW_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])][
        'student_ID'].nunique()
    second_DFW_proportion = second_DFW_number / len(grouped_second_attempters_df['student_ID'].unique()) if len(
        grouped_second_attempters_df) > 0 else 0

    # Step 4: Print the results
    #print(f"Number of students who passed the second attempt of {course_name}: {second_pass_number}")
    #print(f"Number of students who failed the second attempt of {course_name}: {second_DFW_number}")

    # Return the results
    ## FUTURE DEVELOPMENT: add proportions for key demographics here if pie_flag is provided as function parameter
    ##if (node_pie):
    ##    first_attempt_node = pydot.Node("T1", shape="circle", style="wedged",
    ##                                    fillcolor=f"blue;{first_attempt_proportion_female}:green")
    ##    second_attempt_node = pydot.Node("T2", shape="circle", style="wedged",
    ##                                     fillcolor=f"blue;{second_attempt_proportion_female}:green")
    ##else:
    ##    first_attempt_node = pydot.Node("T1", shape="box")
    ##    second_attempt_node = pydot.Node("T2", shape="box")

    descriptives = {
        "first_pass_number": first_pass_number,
        "first_pass_proportion": first_pass_proportion,
        "first_DFW_number": first_DFW_number,
        "first_DFW_proportion": first_DFW_proportion,
        "proportion_DFW_repeat": proportion_DFW_repeat,
        "second_attempt_number" : second_attempt_number,
        "second_pass_number": second_pass_number,
        "second_pass_proportion": second_pass_proportion,
        "second_DFW_number": second_DFW_number,
        "second_DFW_proportion": second_DFW_proportion
    }

    return descriptives

#2023-10-28 Paul Ulrich, generated with ChatGPT4.0
def calculate_alternate_entry(course_name, df, major_matriculation, prerequisite_course = False):
    """
    Calculate the number of students who entered a course through an alternate entry pathway.

    Parameters
    ----------
    course_name : str
        The name of the course for which alternate entry is being calculated.
    df : pandas DataFrame
        The DataFrame containing student enrollment data.
    major_matriculation : str
        The major matriculation of the students being considered.
    prerequisite_course : str, optional
        The name of the prerequisite course, if applicable. Default is False. (e.g. 'Precalculus')

    Returns
    -------
    tuple
        A tuple containing the number of alternate entry students and a list of their Student_IDs.

    Notes
    -----
    This function calculates the number of students who are enrolled in the specified course but have not
    completed the prerequisite course, if provided. It considers students based on their major matriculation.

    This documentation was generated by ChatGPT3.5 using the function code, but I have not checked documentation for accuracy yet.

    Examples
    --------
    >>> number, students = calculate_alternate_entry('Course B', df, 'Computer Science', 'Course A')
    >>> print(f"Number of alternate entry students for Course B: {number}")
    Number of alternate entry students for Course B: 10
    >>> print(f"Student IDs for alternate entry students: {students}")
    Student IDs for alternate entry students: ['ID001', 'ID002', ...]
    """

    # Get students who are in the course but not in the prerequisite course
    #print(f'course_name : {course_name}')
    #print(f'major_matriculation : {major_matriculation}')
    #print(f'prerequisite_course : {prerequisite_course}')
    #print(df['major_matriculation'].unique())

    students_in_course = df[(df['course_title'] == course_name) & (df['major_matriculation'] == major_matriculation)]['student_ID'].unique()
    #print(students_in_course)
    #print(f"Number of unique students in course {course_name}: ", len(students_in_course))

    if prerequisite_course:
        # print(df['Reg_Crse_Title'].unique())
        students_in_prerequisite = set(df[df['course_title'] == prerequisite_course]['student_ID'].unique())
        #print(students_in_prerequisite)
        #print(f"Number of unique students in prerequisite {prerequisite_course}: ", len(students_in_prerequisite))
        alternate_entry_students = [student for student in students_in_course if student not in students_in_prerequisite]
        #print(f"Number of alternate entry students for {course_name}: ", len(alternate_entry_students))
        #print("Student_ID for alternate_entry students : \n", alternate_entry_students)

    # Calculate proportion and number
    #proportion_alternate_entry = len(alternate_entry_students) / len(students_in_course) if len(students_in_course) > 0 else 0
    number_alternate_entry = len(alternate_entry_students)

    return number_alternate_entry, alternate_entry_students

#2023-10-28 Paul Ulrich, generated with ChatGPT4.0
# 2024-01-19 Paul Ulrich, updated with corrected filtering
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

     Notes
     -----
     This function calculates the progression of students from a current course to a next course based on their major matriculation.
     It analyzes second attempts, counts the number of students who passed or failed the current course, and checks how many of
     those who passed the current course did not take the next course.

     This documentation was generated by ChatGPT3.5 using the function code, but I have not checked documentation for accuracy yet.

     Examples
     --------
     >>> proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, did_take_next = \
         calculate_progression_to_next_course('Course A', 'Course B', df, 'Computer Science')
     >>> print(f"Number of students who passed Course A but did not take Course B: {number_not_taking_next}")
     Number of students who passed Course A but did not take Course B: 10
     >>> print(f"Proportion of students who passed Course A and took Course B: {proportion_taking_next}")
     Proportion of students who passed Course A and took Course B: 0.8
     """

    df = df[df['major_matriculation'] == major_matriculation]
    # Step 1: Filter the DataFrame to include only rows where 'Reg_Crse_Title' is equal to 'current_course'
    #print("Current course is:", current_course)
    filtered_df = df[df['course_title'] == current_course]
    # Step 2: Filter to include only those students who attempted the course more than once for the second attempt analysis
    grouped_second_attempters_df = filtered_df.groupby('student_ID').filter(lambda x: len(x) > 1)

    # Step 3: Filter to include only the rows corresponding to the second attempt
    second_attempt_df = grouped_second_attempters_df.groupby('student_ID').nth(1)

    # Step 4: Count the number of students who passed and failed in their second attempts
    second_attempt_pass_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['A', 'B', 'C'])][
        'student_ID'].nunique()
    second_attempt_DFW_number = second_attempt_df[second_attempt_df['course_grade_letter_simp'].isin(['D', 'F', 'W'])][
        'student_ID'].nunique()

    # Step 4: Print the results
    #print(f"Number of students who passed the second attempt of {current_course}: {second_attempt_pass_number}")
    #print(f"Number of students who failed the second attempt of {current_course}: {second_attempt_DFW_number}")

    # Step 1: Get students who passed the current course
    passed_students = df[(df['course_title'] == current_course) & (df['course_grade_letter_simp'].isin(['A', 'B', 'C']))]['student_ID'].unique()
    #print(f"Total number of students who passed {current_course}: ", len(passed_students))

    # Step 2: Check how many of these students did not take the next course
    did_not_take_next = [student for student in passed_students if student not in df[(df['course_title'] == next_course)]['student_ID'].unique()]
    # print("Did NOT take next:")
    # print(did_not_take_next)
    did_take_next = [student for student in passed_students if student in df[(df['course_title'] == next_course)]['student_ID'].unique()]
    # print("Did take next:")
    # print(did_take_next)
    # Filter the DataFrame to include only students who passed and took the next course
    exploratory_df = df[(df['student_ID'].isin(did_take_next)) & (df['course_title'] == current_course)]
    second_attempts_dfw = exploratory_df.groupby('student_ID').filter(lambda x: len(x) == 2 and not any(x['course_grade_letter_simp'].isin(['A', 'B', 'C'])))

    #print("Number of students who got a D, F, or W in their second attempt in", current_course, "and took", next_course, ":", len(second_attempts_dfw['student_ID'].unique()))
    #print(f'Number of students who passed {current_course} and took {next_course} : ', len(did_take_next))

    # Step 3: Calculate proportion and number
    proportion_not_taking_next = len(did_not_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_not_taking_next = len(did_not_take_next)
    proportion_taking_next = len(did_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_taking_next = len(did_take_next)
    print(f"Number of students who passed {current_course} but did not take {next_course} : ", number_not_taking_next)
    #print(f"Proportion of students who passed but did not take {next_course} : ", proportion_not_taking_next)
    return proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, did_take_next

# 2023-10-28 (PNU, modified as extension from course_attempts_pydot() with ChatGPT4.0):
# uses data from combine_course_grades_with_demographics() to determine proportions of students who passed course
# course_sequence : list of strings representing names of courses of interest (e.g., "CALC FOR THE LIFE SCIENCES I")
# df : dataframe containing grades and demographics
# major_matriculation: string, code for major (e.g., "BIO")
# [not implemented yet] node_pie: boolean; optional parameter that can be used to demonstrate population stats (like % female) for a specific node
def course_sequence_analysis(course_sequence, df, major_matriculation, node_pie = False):
    """
     Analyze the progression of students through a sequence of courses.

     Parameters
     ----------
     course_sequence : list of str
         The sequence of courses to analyze.
     df : pandas DataFrame
         The DataFrame containing student enrollment data.
     major_matriculation : str
         The major matriculation of the students being considered.
     node_pie : bool, optional
         Whether to include pie charts in the node labels (default is False).

     Returns
     -------
     None

     Notes
     -----
     This function analyzes the progression of students through a sequence of courses. It creates a directed graph where nodes represent
     courses and edges represent various student outcomes such as passing, retaking, or not taking the next course. The graph is saved
     as an image and displayed.

     This documentation was generated by ChatGPT3.5 using the function code, but I have not checked documentation for accuracy yet.

     Examples
     --------
     >>> course_sequence_analysis(['Course A', 'Course B', 'Course C'], df, 'Computer Science')
     """

    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    #next_course_name = course_sequence[1]
    previous_pass_node = None

    #Use MATRIC_TERM value associated with earliest 'TERM' for the 'Student_ID'
    #Could be better to drag this in from demographics?
    # Sort the DataFrame by 'student_ID' and 'course_term' in ascending order
    df_sorted = df.sort_values(by=['student_ID', 'course_term'])
    # Group by 'Student_ID' and get the row with the lowest 'TERM' for each group
    earliest_major = df_sorted.groupby('student_ID').first()['major_matriculation']
    # Merge the result back to the original DataFrame based on 'Student_ID'
    df_merged = df.merge(earliest_major, how='left', on='student_ID', suffixes=('', '_Earliest'))
    # Fill missing values in 'major_matriculation' with the corresponding values from 'major_matriculation_Earliest'
    df_merged['major_matriculation'] = df_merged['major_matriculation_Earliest'].fillna(
        df_merged['major_matriculation'])
    # Drop the auxiliary column 'major_matriculation_Earliest'
    df_merged.drop(columns=['major_matriculation_Earliest'], inplace=True)
    df = df_merged.copy()


    for index, course_name in enumerate(course_sequence):
        print(index)

        # Create nodes for the course
        course_node = pydot.Node(course_name, shape="box")
        pass_node = pydot.Node(f"Pass {course_name}", label="Pass")
        dfw_node = pydot.Node(f"DFW {course_name}", label="DFW")
        retake_node = pydot.Node(f"Retake {course_name}", label="Retake")
        if index < len(course_sequence) - 1:
            did_not_take_next_node = pydot.Node(f"Did Not Take Next {course_name}", label="Did Not Take Next")

        # Add nodes to the graph
        graph.add_node(course_node)
        graph.add_node(pass_node)
        graph.add_node(dfw_node)
        graph.add_node(retake_node)
        if index < len(course_sequence) - 1:
            graph.add_node(did_not_take_next_node)

        # Analyze the course
        if index == 0:  #if the course is the first in the sequence list
            descriptives = analyze_course(course_name, df, major_matriculation)
            #next_course_name = course_sequence[index + 1]
            proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, students_who_did_take_next = calculate_progression_to_next_course(
                current_course = course_name, next_course = course_sequence[index + 1], df = df, major_matriculation = major_matriculation)
            #print("Results are , ", proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next)
            next_course_name = course_sequence[index + 1]
            print("Next course name : ", next_course_name)
            # proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, students_who_did_take_next = calculate_not_taking_next(
            #    course_name, next_course_name, df, major_matriculation)
            print("Number taking next : ", number_taking_next)
            graph.add_edge(pydot.Edge(pass_node, did_not_take_next_node,
                                      label=f"{proportion_not_taking_next:.3f} ({number_not_taking_next})"))

        # if the course is not the first in the sequence list or the last in the list
        if index > 0:
            prerequisite_course_name = course_sequence[index - 1]
            print("The prerequisite course name is ", prerequisite_course_name, "and current course is",
                  course_sequence[index])
            if index < (len(course_sequence) - 1):
                #determine which students entered the course through an alternate route
                number_alternate_entry, students_in_alternate_entry = calculate_alternate_entry(course_name, df, major_matriculation, prerequisite_course_name)

                #determine how many students came from the prerequisite course and edge connecting prior course to current course
                prerequisite_course_results = calculate_progression_to_next_course(
                    current_course = prerequisite_course_name, next_course = course_name, df = df, major_matriculation = major_matriculation)
                graph.add_edge(pydot.Edge(previous_pass_node, course_node,
                                          label=f"{prerequisite_course_results[2]:.3f} ({prerequisite_course_results[3]})"))

                # for downstream courses, we only want to look at students who either passed the first course or came in through alternate edge
                # Universities occasionally permit students with a non-passing prereq score to take the next course. In the future, we may
                # want these students to be illustrated as a separate edge from the DFW node in the prereq into the second course,
                # but at this point (2024-02-21), they are being excluded

                #analyze the course with only those students who passed and took the subsequent course or came in via alternate route
                current_course_df = df[(df['student_ID'].isin(students_who_did_take_next)) | (df['student_ID'].isin(students_in_alternate_entry))]
                print(course_name)
                descriptives = analyze_course(course_name, current_course_df, major_matriculation, course_sequence[
                    index])  ## 2024-02-21 I don't think the last parameter does anything yet
                #print(descriptives)

            if (index == (len(course_sequence) - 1)):
                print("INDEX IS...", index)
                prerequisite_course_name = course_sequence[index - 1]
                # determine which students entered the course through an alternate route
                number_alternate_entry, students_in_alternate_entry = calculate_alternate_entry(course_name, df,
                                                                                                major_matriculation,
                                                                                                prerequisite_course_name)

                # determine how many students came from the prerequisite course and edge connecting prior course to current course
                prerequisite_course_results = calculate_progression_to_next_course(
                    current_course=prerequisite_course_name, next_course=course_name, df=df,
                    major_matriculation=major_matriculation)
                graph.add_edge(pydot.Edge(previous_pass_node, course_node,
                                          label=f"{prerequisite_course_results[2]:.3f} ({prerequisite_course_results[3]})"))

                # analyze the course with only those students who passed and took the subsequent course or came in via alternate route
                current_course_df = df[(df['student_ID'].isin(students_who_did_take_next)) | (
                    df['student_ID'].isin(students_in_alternate_entry))]
                print(course_name)
                descriptives = analyze_course(course_name, current_course_df, major_matriculation, course_sequence[
                    index])  ## 2024-02-21 I don't think the last parameter does anything yet


        # Create edges and set labels with limited significant figures
        print(descriptives)
        graph.add_edge(pydot.Edge(course_node, pass_node, label=f"{descriptives['first_pass_proportion']:.3f} ({descriptives['first_pass_number']})"))
        graph.add_edge(pydot.Edge(course_node, dfw_node, label=f"{descriptives['first_DFW_proportion']:.3f} ({descriptives['first_DFW_number']})"))
        graph.add_edge(pydot.Edge(dfw_node, retake_node, label=f"{descriptives['proportion_DFW_repeat']:.3f} ({descriptives['second_attempt_number']})"))
        if index < (len(course_sequence) - 1):
            graph.add_edge(pydot.Edge(dfw_node, did_not_take_next_node, label=f"{1-descriptives['proportion_DFW_repeat']:.3f} ({descriptives['first_DFW_number'] - descriptives['second_attempt_number']})"))
            graph.add_edge(pydot.Edge(retake_node, did_not_take_next_node, label=f"{descriptives['second_DFW_proportion']:.3f} ({descriptives['second_DFW_number']})"))
        graph.add_edge(pydot.Edge(retake_node, pass_node, label=f"{descriptives['second_pass_proportion']:.3f} ({descriptives['second_pass_number']})"))

        # Return the results
        ## FUTURE DEVELOPMENT: add proportions for key demographics here if pie_flag is provided as function parameter
        ##if (node_pie):
        ##    first_attempt_node = pydot.Node("T1", shape="circle", style="wedged",
        ##                                    fillcolor=f"blue;{first_attempt_proportion_female}:green")
        ##    second_attempt_node = pydot.Node("T2", shape="circle", style="wedged",
        ##                                     fillcolor=f"blue;{second_attempt_proportion_female}:green")
        ##else:
        ##    first_attempt_node = pydot.Node("T1", shape="box")
        ##    second_attempt_node = pydot.Node("T2", shape="box")

        if (index > 0):
            if(index < (len(course_sequence) - 1)):
                next_course_name = course_sequence[index + 1]
                print("Course name : ", course_name)
                print("Next course name : ", next_course_name)
                proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, students_who_did_take_next = calculate_progression_to_next_course(
                    course_name, next_course_name, df, major_matriculation)
                print("Number not taking next : ", number_not_taking_next)
                graph.add_edge(pydot.Edge(pass_node, did_not_take_next_node, label=f"{proportion_not_taking_next:.3f} ({number_not_taking_next})"))


            # Node and edge for students entering from alternate pathways (tested out, etc)
            prerequisite_course_name = course_sequence[index -1]
            number_alternate_entry, students_in_alternate_entry = calculate_alternate_entry(course_name, df, major_matriculation, prerequisite_course_name)
            print(number_alternate_entry, len(students_in_alternate_entry))
            alternate_entry_node = pydot.Node(f"Alternate Entry to {course_name}", label="Alternate Entry")
            graph.add_node(alternate_entry_node)
            graph.add_edge(pydot.Edge(alternate_entry_node, course_node, label=f"{number_alternate_entry}"))

        previous_pass_node = pass_node

    # Set graph attributes
    graph.set("nodesep", "1.0")

    # Save or render the graph
    image_filename = "course_sequence_attempts_graph.png"
    graph.write_png(image_filename)

    # Display the graph
    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Course Sequence Analysis for {major_matriculation} Majors", fontsize=16)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()


def track_major_change(initial_demographics_df, demographics_df, range_first_term_start = 200501, range_first_term_stop = 203001, matric_term_earliest = 200501, initial_major='BIO'):
    """
    Track students who started with a specified major and then changed
    to another specified major by the fall of their 3rd year.

    Parameters:
    - initial_demographics_df (pd.DataFrame): DataFrame containing demographics from the first semester students took classes.
    - demographics_df (pd.DataFrame): Larger DataFrame containing demographics for all semester data.
    - initial_major (str): The students major declared their first semester (e.g., 'CHM')
    - range_first_term_stop (int): Term code (YYYYMM) representing the last semester a student could have started courses.
    - range_first_term_start (int): Term code (YYYYMM) representing the first semester of interest a student could have started courses.
    - matric_term_earliest (int): Term code (YYYYMM) representing the earliest matriculation term that will be included in the dataset.

    Returns:
    - pd.DataFrame: DataFrame with students' initial major, major in fall of 3rd year, graduation status, sex, race, ethnicity, birth year, and GPA at the first semester.
    """
    # Filter for students with the specified initial major
    filtered_initial_demographics_df = initial_demographics_df[(initial_demographics_df['major_term'] == initial_major) & (initial_demographics_df['demographics_term'] <= range_first_term_stop) &(initial_demographics_df['demographics_term'] >= range_first_term_start) & (initial_demographics_df['term_matriculation'] >= matric_term_earliest)].copy()

    # Calculate the expected term for the fall of the 3rd year
    filtered_initial_demographics_df['Year'] = filtered_initial_demographics_df['demographics_term'] // 100
    filtered_initial_demographics_df['ThirdYearFallTerm'] = (filtered_initial_demographics_df['Year'] + 2) * 100 + 8

    # Use this term and Student_ID to filter the larger demographics_df
    third_year_df = demographics_df[demographics_df.set_index(['student_ID', 'demographics_term']).index.isin(
        filtered_initial_demographics_df.set_index(['student_ID', 'ThirdYearFallTerm']).index)]

    # Merge initial_df with third_year_df
    result_df = filtered_initial_demographics_df.merge(third_year_df, on='student_ID', suffixes=('', '_3rdYear'), how = "left")

    # Identify students who don't have a third-year entry
    missing_third_year = result_df['major_term_3rdYear'].isna()
    missing_count = missing_third_year.sum()
    print(f"{missing_count} students don't have a corresponding demographic entry for Fall of their third year.")

    return result_df[['demographics_term', 'student_ID', 'BirthYear', 'SDSTUDEMOG_ETHNICITY_CODE', 'demographics_race', 'demographics_sex','major_term', 'SDSTUGPA_GPA_INST', 'term_matriculation', 'major_term_3rdYear', 'Grad_year', 'Grad_term', 'Degree']]



def glm_retention_analysis(demographics_df, math_grades_df, major_matriculation, reference_course='PRECALCULUS', left = 0):
    """
    Perform a Generalized Linear Model (GLM) analysis of retention within the university at year 3 as a function of their first mathematics
    course and other variables.

    Parameters:
    - demographics_df (DataFrame): DataFrame containing demographic information.
    - math_grades_df (DataFrame): DataFrame containing math grades information.
    - major_matriculation (str): students major code at matriculation (e.g., 'CHM').
    - reference_course (str): Reference course for generating dummy variables. (e.g., 'PRECALCULUS')
    - left (int): Flag indicating the type of analysis:
        - 0 (default): Retention analysis, prediction of retention at the university by Fall of 3rd academic year.
        - 1: Predicting students leaving the university.

    Returns:
    - results_GLM (GLMResults): GLM results object.
    """

    math_grades_df = math_grades_df[math_grades_df['major_matriculation'] == major_matriculation]

    # convert 'demographics_sex' data  to categorical where 'F' = 1, 'M' = 0, and 'N' = 2
    # TODO address non-binary sex codes if datasets have sufficient sample size to accommodate
    math_grades_df.loc[:, 'demographics_sex'] = math_grades_df['demographics_sex'].replace(
        {'F': 1, 'M': 0, 'N': 2}).astype(int)

    #print(math_grades_df['demographics_sex'].unique())
    demographics_df = demographics_df.dropna(subset=['demographics_sex'])  # Drop rows with NaN values in the 'demographics_sex' column
    demographics_df.loc[:,'demographics_sex'] = demographics_df['demographics_sex'].replace({'F': 1, 'M': 0, 'N': 2}).astype(
        int)

    #print(demographics_df['demographics_sex'].unique())

    print("Length of major_demographics_df input = ", len(demographics_df), " and number of unique students = ",
          len(demographics_df['student_ID'].unique()))

    # Merge with math grades using the earliest math course record for each student
    mask = math_grades_df.groupby('student_ID')['course_term'].idxmin()
    first_math_course_df = math_grades_df.loc[mask]
    merged_df = demographics_df.merge(first_math_course_df, on='student_ID', how='left', suffixes=('', '_y'))

    merged_df = merged_df[~(merged_df['demographics_term'] > merged_df['course_term'])]

    print("Length of merged_df after merge with first_math_course_df = ", len(merged_df),
          " and number of unique students = ",
          len(merged_df['student_ID'].unique()))

    merged_df = merged_df[~merged_df.duplicated(subset=['student_ID', 'demographics_high_school_GPA'], keep='first')]

    # merged_df = merged_df[~merged_df['HS_AVERAGE_y'].isnull()]
    print("Length of merged_df after merge with df_hsgpa and removal of duplicates = ", len(merged_df),
          " and number of unique students = ", len(merged_df['student_ID'].unique()))

    # Create flags for major retention by the 3rd year and if the student left
    merged_df['Major_Retention_3rdYear'] = (
                merged_df['major_term_3rdYear'] == merged_df['major_matriculation']).astype(int)
    merged_df['left_by_3rdYear_flag'] = merged_df['major_term_3rdYear'].isnull().astype(int)

    # Calculate number of months from start of first semester to the start of the semester of first math course
    merged_df['Months_Difference'] = ((merged_df['course_term'] // 100 - merged_df[
        'demographics_term'] // 100) * 12) + (merged_df['course_term'] % 100 - merged_df['demographics_term'] % 100)

    # Exclude students who never took one of the math courses
    merged_df = merged_df[~merged_df['Months_Difference'].isnull()]
    print("After excluding those who never took a math course ", len(merged_df))

    # Drop rows without high school GPA data or who left by 3rd year
    merged_df = merged_df.dropna(subset=['demographics_high_school_GPA'])
    print("After excluding those who don't have a HS GPA: ", len(merged_df))

    # Exclude honor courses
    merged_df = merged_df[~merged_df['course_title'].str.contains(r'\bhon\b', case=False, na=False)]
    print("After excluding students in honors sections: ", len(merged_df))

    # Exclude rows without 'SDSTUGPA_GPA_INST' values
    merged_df = merged_df[~merged_df['SDSTUGPA_GPA_INST'].isna()]
    print("After excluding students with no institutional GPA for their first semester: ", len(merged_df))

    # if we are interested in retention in the major at 3rd year, run GLM with 'Major_Retention_3rdYear' as response variable
    if(left == 0):
        remained_df = merged_df[merged_df['left_by_3rdYear_flag'] == 0]
        print("After excluding those who left by 3rd year: ", len(remained_df))

        # Generate dummy variables for course titles excluding the reference course
        course_title_dummies = pd.get_dummies(remained_df['course_title'], prefix='Course')
        course_title_sample_sizes = course_title_dummies.sum().to_dict() #this is calculated BEFORE dropping the PRECALC reference course
        course_title_dummies.drop(f'Course_{reference_course}', axis=1, inplace=True)

        # Prepare the final DataFrame for GLM
        X = remained_df[['demographics_sex', 'demographics_age', 'flag_first_generation', 'flag_PELL', 'SDSTUGPA_GPA_INST','Months_Difference', 'demographics_high_school_GPA']].join(course_title_dummies)
        y = remained_df['Major_Retention_3rdYear']

        # Convert boolean columns to 'int64' if any
        X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})

        # Ensure that 'demographics_high_school_GPA' and 'demographics_sex' are in GLM-compatible types
        X['demographics_high_school_GPA'] = X['demographics_high_school_GPA'].astype(float)
        X['demographics_sex'] = X['demographics_sex'].astype(int)

        # Drop 'course_title' column if it's still present
        if 'course_title' in X.columns:
            X = X.drop('course_title', axis=1)

        # Fit the GLM
        model = sm.GLM(y, X, family=sm.families.Binomial())
        results_GLM = model.fit()
        print('\n', results_GLM.summary(), '\n')

        # Extract coefficients from the summary table and report fold changes
        coefficients = results_GLM.params
        p_values = results_GLM.pvalues
        fold_changes = np.exp(coefficients)
        print('Fold changes for significant (alpha =  0.05) predictors:')
        significant_predictors = (p_values<= 0.05)
        for predictor, fold_change in fold_changes[significant_predictors].items():
            print(f"{predictor}, Fold Change: {round(fold_change,2)}")


        # Print sample sizes
        sex_sample_sizes = X.groupby('demographics_sex').size().to_dict()
        first_gen_sample_sizes = X.groupby('flag_first_generation').size().to_dict()
        pell_sample_sizes = X.groupby('flag_PELL').size().to_dict()
        print('\nSample sizes:')
        print("...by course title:")
        print(course_title_sample_sizes, '\n')
        print("...by sex:")
        print(sex_sample_sizes, '\n')
        print("...by first generation:")
        print(first_gen_sample_sizes, '\n')
        print("...by pell eligibility:")
        print(pell_sample_sizes, "\n ----------------------------------- \n")
        return results_GLM


    #if we are interested in predictors of students leaving the university,run the GLM with 'left_by_3rdYear_flag' as response variable
    if (left == 1):
        left_df = merged_df

        # Generate dummy variables for course titles excluding the reference course
        course_title_dummies = pd.get_dummies(left_df['course_title'], prefix='Course')
        course_title_sample_sizes = course_title_dummies.sum().to_dict() #this is calculated BEFORE dropping the PRECALC reference course
        course_title_dummies.drop(f'Course_{reference_course}', axis=1, inplace=True)

        # Prepare the final DataFrame for GLM
        X = left_df[['demographics_sex', 'demographics_age', 'flag_first_generation', 'flag_PELL', 'SDSTUGPA_GPA_INST', 'Months_Difference', 'demographics_high_school_GPA']].join(
            course_title_dummies)
        y = left_df['left_by_3rdYear_flag']

        # Convert boolean columns to 'int64' if any
        X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})

        # Ensure that 'demographics_high_school_GPA' and 'demographics_sex' are in GLM-compatible types
        X['demographics_high_school_GPA'] = X['demographics_high_school_GPA'].astype(float)
        X['demographics_sex'] = X['demographics_sex'].astype(int)


        # Drop 'course_title' column if it's still present
        if 'course_title' in X.columns:
            X = X.drop('course_title', axis=1)

        # Fit the GLM
        model = sm.GLM(y, X, family=sm.families.Binomial())
        results_GLM = model.fit()
        print("\n\n")
        print(results_GLM.summary(), "\n")

        # Extract coefficients from the summary table and report fold changes
        coefficients = results_GLM.params
        p_values = results_GLM.pvalues
        fold_changes = np.exp(coefficients)
        print('Fold changes for significant (alpha =  0.05) predictors:')
        significant_predictors = (p_values <= 0.05)
        for predictor, fold_change in fold_changes[significant_predictors].items():
            print(f"{predictor}, Fold Change: {round(fold_change, 2)}")

        # Print sample sizes
        sex_sample_sizes = X.groupby('demographics_sex').size().to_dict()
        first_gen_sample_sizes = X.groupby('flag_first_generation').size().to_dict()
        pell_sample_sizes = X.groupby('flag_PELL').size().to_dict()
        print('\nSample sizes:')
        print("...by course title:")
        print(course_title_sample_sizes, '\n')
        print("...by sex:")
        print(sex_sample_sizes, '\n')
        print("...by first generation:")
        print(first_gen_sample_sizes, '\n')
        print("...by pell eligibility:")
        print(pell_sample_sizes, "\n ----------------------------------- \n")

        return results_GLM

def plot_attempt_descriptive_stats(data, course_prefix, course_number, max_attempts=4, return_results=0):
    """
        Plot descriptive statistics and box plots for course attempts. NOTE: withdrawals are not included in the output

        Parameters
        ----------
        data : pandas.DataFrame
            Input DataFrame containing course data.
        course_prefix : str
            Prefix of the course (e.g., CHEM)
        course_number : int
            Number of the course (e.g., 2211)
        max_attempts : int, optional
            Maximum number of attempts (default is 4).
        return_results : int, optional
            Indicator for whether to return results as a DataFrame (default is 0, no results returned).

        Returns
        -------
        pandas.DataFrame or None
            DataFrame containing student ID, attempt number, and course grade numeric if `return_results` is 1,
            otherwise None.

        Notes
        -----
        This function filters the input DataFrame to include only the specified course number and excludes withdrawals
        (coded as -1) that could skew results. It then calculates descriptive statistics for each attempt and generates
        box plots to visualize the distribution of course grades across attempts.

        Example usage:
        plot_attempt_descriptive_stats(math_1111_1113, course_prefix='MATH', course_number=1111, max_attempts=3, return_results=1)
        """

    # Filter the data to include only the specified course number and exclude withdrawals (coded as -1) that would skew results
    course_data = data[
        (data['course_prefix'] == course_prefix) & (data['course_number'] == course_number) & (data['course_grade_numeric'] != -1)]
    course_data = course_data.sort_values(by=['student_ID', 'course_term'], ascending=[True, True])

    # Initialize an empty list to store the sorted data
    data_list = []

    # Group the data by 'Student_ID'
    grouped_data = course_data.groupby('student_ID')

    # Initialize lists to store descriptive statistics for each attempt
    descriptive_stats_list = [[] for _ in range(max_attempts)]

    # Loop through grouped data to calculate and store descriptive statistics for each attempt
    for student_id, group in grouped_data:
        for attempt in range(1, max_attempts + 1):
            if len(group) >= attempt:
                attempt_data = group.iloc[attempt - 1]
                descriptive_stats_list[attempt - 1].append(attempt_data['course_grade_numeric'])
                if return_results:
                    data_list.append([student_id, attempt, attempt_data['course_grade_numeric']])

    # Print descriptive statistics for each attempt
    #for i, stats in enumerate(descriptive_stats_list):
    #    print(f'Descriptive statistics for {i + 1} Attempt:')
    #    print(pd.Series(stats).describe())
    #    print()

    # Calculate descriptive statistics for each attempt
    # descriptive_stats = [pd.Series(stats).describe() for stats in descriptive_stats_list]

    # Create box and whisker plots for each attempt
    plt.figure(figsize=(12, 8))
    #
    plt.boxplot(descriptive_stats_list, labels=[f'{i} Attempt' for i in range(1, max_attempts + 1)])
    plt.boxplot(descriptive_stats_list,
                labels=[f'{i}\n (n = {len(stats)})' for i, stats in enumerate(descriptive_stats_list, start=1)])

    plt.title(f'Descriptive Statistics for {course_prefix} {course_number}', fontsize=24)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('Attempt Number', fontsize=20)
    plt.ylabel('Course GPA', fontsize=20)

    plt.show()

    # Create a DataFrame from the collected data
    columns = ['student_ID', 'Attempt', 'course_grade_numeric']

    # send back data
    if return_results:
        return pd.DataFrame(data_list, columns=columns)

def glm_effect_of_taking_classes_simultaneously(input_df, dependent_course_prefix, dependent_course_number, predictor_course_prefix, predictor_course_numbers, predictor_high_school_GPA = 0, predictor_sex = 0, predictor_transfer_credit = 0, predictor_first_generation = 0, predictor_pell = 0, associates_program_code = None, dependent_course_suffix = None):
    """
    Generalized Linear Model (GLM) for effect of taking certain courses on performance in a dependent course.

    Parameters
    ----------
    input_df : pandas.DataFrame
        Input DataFrame containing course data.
    dependent_course_prefix : str
        Prefix of the dependent course (e.g., 'CHEM' or 'BIOL').
    dependent_course_number : int
        Number of the dependent course (e.g., 1211).
    predictor_course_prefix : str
        Prefix of the predictor courses (e.g., 'CHEM' or 'BIOL').
    predictor_course_numbers : list
        Numbers of the predictor courses (e.g., ['1211', '1212', '1213']).
    predictor_high_school_GPA : int, optional
        Indicator for whether high school GPA is used as a predictor (default is 0).
    predictor_transfer_credit : int, optional
        Indicator for whether transfer credits are considered (default is 0, not included).
    associates_program_code : str or None, optional
        Code representing the associate's program (default is None).
    dependent_course_suffix : str or None, optional
        Suffix of the dependent course (default is None) (e.g., 'K' or 'L').

    Returns
    -------
    None

    Raises
    ------
    KeyError
        If any required column is missing from the DataFrame.

    Notes
    -----
    This function fits a Generalized Linear Model (GLM) to assess the effect of taking certain courses simultaneously on the performance in a dependent course. It preprocesses the input DataFrame, filtering rows, handling missing values, and creating necessary flags for analysis. Then, it fits the GLM model and calculates sample sizes for each course combination.

    """

    dependent_course_number = int(dependent_course_number)

    # Drop rows with 'course_grade_letter' == 'nan'
    input_df = input_df[~(input_df['course_grade_letter'] == 'nan')]

    # Remove duplicate rows
    input_df = input_df[~input_df.duplicated(
        subset=['student_ID', 'course_term', 'course_prefix', 'course_suffix', 'course_number', 'course_grade_letter'],
        keep='first')]

    # Create 'flag_course_associates' column in the event that course attempts in a non-bachelor's program can be excluded
    if (associates_program_code):
        input_df['flag_course_associates'] = (input_df['course_college'] == associates_program_code).astype(int)

    # Default behavior does does not use first generation as a predictor unless predictor_first_generation == 1
    if(predictor_first_generation == 1):
        input_df['flag_first_generation'].replace({'Y': 1, np.nan: 0}, inplace=True)

    # Default behavior does does not use Pell status as a predictor unless predictor_first_generation == 1
    if(predictor_pell == 1):
        input_df['flag_PELL'].replace({'Y': 1, np.nan: 0}, inplace=True)

    # Default behavior is to eliminate students from dataset who matriculate with transfer hours
    if (predictor_transfer_credit == 0):
        #print(input_df['transfer_hours_matriculation'].unique())
        input_df = input_df[~(input_df['transfer_hours_matriculation'] > 0)]

    # If high school GPA is indicated as a predictor for the model, then all rows without high school GPA should be dropped
    if (predictor_high_school_GPA == 1):
        # print(input_df['demographics_high_school_GPA'].unique())
        input_df['demographics_high_school_GPA'] = pd.to_numeric(input_df['demographics_high_school_GPA'], errors='coerce')
        input_df = input_df[~(input_df['demographics_high_school_GPA'].isna())]
        # print(input_df['demographics_high_school_GPA'].unique())

    dependent_course_df = pandas.DataFrame

    if (dependent_course_suffix is None):
        # Filter rows for the specified course_prefix, number, and suffix
        dependent_course_df = input_df[(input_df['course_prefix'] == dependent_course_prefix) &
                               (input_df['course_number'] == dependent_course_number)]
        # Find the earliest 'course_term' for each 'student_ID' in the dependent_course_df
        dependent_course_earliest_terms = dependent_course_df.groupby('student_ID')['course_term'].min().reset_index()
        print(len(dependent_course_df))

    # if data source includes courses with lab/lecture combined (at GSU, this could be CHEM 1212K) or separate lab and lecture (at GSU, CHEM 1212 lecture and CHEM 1212L laboratory)
    # and dependent_course_suffix is not empty, then exclude all instances where students took these courses via separated format
    elif(dependent_course_suffix):
        # Filter rows for the specified course_prefix, number, and suffix
        dependent_course_df = input_df[(input_df['course_prefix'] == dependent_course_prefix) &
                                       (input_df['course_number'] == dependent_course_number) &
                                       (input_df['course_suffix'] == dependent_course_suffix)]

        # Find the earliest 'course_term' for each 'student_ID' in the dependent_course_df
        dependent_course_earliest_terms = dependent_course_df.groupby('student_ID')['course_term'].min().reset_index()

        non_combined_course_df = input_df[(input_df['course_prefix'] == dependent_course_prefix) &
                                    (input_df['course_number'] == dependent_course_number) &
                                    (input_df['flag_course_associates'] == 1)]  # this captures ALL rows of the dependent ocurse taken via an associates program

        # Find the earliest 'TERM' for each 'Student_ID' for the specified course
        non_combined_course_earliest_terms = non_combined_course_df.groupby('student_ID')['course_term'].min().reset_index()

        # Merge the earliest 'course_term' values for both the specified course and course with course suffix
        merged_terms = pd.merge(dependent_course_earliest_terms, non_combined_course_earliest_terms, on='student_ID', how='left')

        # Filter out rows where 'course_term_x' is later than 'course_term_y'for the specified course course suffix
        filtered_result_df = merged_terms[merged_terms['course_term_x'] <= merged_terms['course_term_y']]
        print("Number of students before exclusion of those who took it before : ", len(dependent_course_df))

        # Exclude students who took the specified course before
        dependent_course_df = dependent_course_df[~dependent_course_df['student_ID'].isin(filtered_result_df['student_ID'])]
        print("Number of students after exclusion of those who took it before : ", len(dependent_course_df))

    # Group the data by 'Student_ID'
    grouped_data = dependent_course_df.groupby('student_ID')

    # Calculate the minimum 'TERM' value for the specified course for each student
    min_term_by_student = grouped_data.apply(lambda group: group[group['course_number'] == dependent_course_number]['course_term'].min())

    # Create a flag column based on the minimum 'course_term' value
    dependent_course_df[f'flag_first_attempt_{dependent_course_prefix}_{dependent_course_number}'] = (
        dependent_course_df.groupby('student_ID')['course_term']
        .transform(lambda x: x == min_term_by_student[x.name]).astype(int))

    # Create a DataFrame to store the course data for all students in the predictor courses
    predictor_courses_df = input_df[(input_df['course_number'].isin(predictor_course_numbers)) & (input_df['course_prefix'] == predictor_course_prefix)]

    # Merge the math course data with the specified course with suffix 'K' on 'Student_ID' and 'TERM' using a left join
    merged_df = pd.merge(dependent_course_df, predictor_courses_df, on=['student_ID', 'course_term'], how='left', suffixes=('', '_y'))

    print("Number of non-first attempts : ", len(merged_df[merged_df[f'flag_first_attempt_{dependent_course_prefix}_{dependent_course_number}'] == 0]))
    print("Number of first attempts : ", merged_df[f'flag_first_attempt_{dependent_course_prefix}_{dependent_course_number}'].sum())

    # Iterate over math course numbers to create flags
    for predictor_course in predictor_course_numbers:
        # Define a new column name for the flag
        flag_column_name = f'flag_{predictor_course_prefix}{predictor_course}'

        merged_df[flag_column_name] = 0

        # Create a boolean mask for students who took the predictor course during the same term they took the dependent course
        mask = (merged_df['course_number_y'] == predictor_course)

        # Set the flag to 1 for rows that satisfy the condition
        merged_df.loc[mask, flag_column_name] = 1

    # Filter merged_df to keep only the rows where 'Student_ID' appears once
    duplicate_students = merged_df[merged_df.duplicated(subset=['course_term', 'student_ID'])]['student_ID']
    filtered_merged_df = merged_df[~merged_df['student_ID'].isin(duplicate_students)]

    print("Total number of students in filtered_merged_df after dropping of those from merged_df with duplicate 'course_term' and 'student_ID : ",
        len(filtered_merged_df))

    # Filter rows with non-first attempts and negative 'course_grade_numeric' values
    first_attempt_df = filtered_merged_df[filtered_merged_df[f'flag_first_attempt_{dependent_course_prefix}_{dependent_course_number}'] == 1].copy()
    # print(list(first_attempt_df))
    first_attempt_df = first_attempt_df[~(first_attempt_df['course_grade_numeric'] < 0)]
    #print(first_attempt_df)
    #print(list(first_attempt_df))
    print("Total number of first attempts before exclusion of those without demographics_high_school_GPA or course_grade_numeric values = ", len(first_attempt_df))

    # Check if 'demographics_sex' is present in the DataFrame
    if 'demographics_sex' not in first_attempt_df.columns:
        raise KeyError('demographics_sex column is missing from the DataFrame')

    # Convert categorical variables to dummy variables
    first_attempt_df = pd.get_dummies(first_attempt_df, columns=['demographics_sex'], drop_first=True)


    # Create a list of predictor columns
    predictor_columns = []

    # Check if high school GPA is to be included as a predictor
    if(predictor_high_school_GPA == 1):
        predictor_columns.append('demographics_high_school_GPA')

    # Check if sex is to be included as a predictor
    if(predictor_sex == 1):
        predictor_columns.append('demographics_sex_M')

    # Check if first generation is to be included as a predictor
    if(predictor_first_generation == 1):
        predictor_columns.append('flag_first_generation')

    # Check if Pell status is to be included as a predictor
    if predictor_pell == 1:
        predictor_columns.append('flag_PELL')

    # Iterate over predictor course numbers and include them as predictors
    predictor_columns.extend([f'flag_MATH{predictor_course}' for predictor_course in predictor_course_numbers])

    #if(predictor_high_school_GPA == 1):
    #    predictor_columns = ['demographics_high_school_GPA']+['flag_first_generation']+['demographics_sex_M'] + [f'flag_MATH{predictor_course}' for predictor_course in
    #                                                  predictor_course_numbers]
    #else:
    #    predictor_columns = ['demographics_sex_M']+['flag_first_generation']+[f'flag_MATH{predictor_course}' for predictor_course in predictor_course_numbers]

    # Check if the predictors are all in the DataFrame
    missing_predictors = [col for col in predictor_columns if col not in first_attempt_df.columns]
    if missing_predictors:
        raise KeyError(f'The following predictor columns are missing from the DataFrame: {missing_predictors}')

    # Add a constant to the model (intercept)
    X = sm.add_constant(first_attempt_df[predictor_columns])
    X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})
    print("Type of X : ", type(X))
    # Set up the y for the GLM
    y = first_attempt_df['course_grade_numeric']
    print("Type of y : ", type(y))

    # Fit the GLM
    model = sm.GLM(y, X, family=sm.families.Gaussian())
    results_GLM = model.fit()

    # Dictionary to hold the sample sizes for each math course
    sample_sizes = {}

    for predictor_course in predictor_course_numbers:
        flag_column = f'flag_{predictor_course_prefix}{predictor_course}'
        # Sum up the flag column to get the number of students who took the specified math course along with the specified course with suffix 'K'
        sample_sizes[f'{predictor_course_prefix}{predictor_course}'] = first_attempt_df[flag_column].sum()

    none_taken_count = ((first_attempt_df[[f'flag_{predictor_course_prefix}{predictor_course}' for predictor_course in
                                           predictor_course_numbers]] == 0).all(axis=1)).sum()
    sample_sizes['No simultaneously taken course'] = none_taken_count

    # Print results and sample sizes
    print(results_GLM.summary(), "\n\n Sample sizes for each course:", sample_sizes)

    # Uncomment the following if you want to return the processed data frame
    # return first_attempt_df


"""
Plots stacked bar charts of specified proportions by course and major.

This function iterates through each course and creates a stacked bar chart
for each specified proportion within the course. Each bar represents a major,
and the stacks represent the specified proportions within that major.
The charts can be saved to a multi-page PDF if desired.

Args:
    df (DataFrame): The DataFrame containing the course data.
    proportions_to_plot (list of str): The list of proportion column names to be plotted.
    pdf_filename (str, optional): The filename for the output PDF. If None, the charts
                                  will not be saved to a PDF. Default is None.
    save_as_pdf (bool, optional): If True, and a pdf_filename is provided, the charts will
                                  be saved to a multi-page PDF. If False, the charts will
                                  be displayed on screen. Default is False.

Returns:
    None: The function does not return a value. It either saves the charts to a PDF or displays them on screen.

Example:
    plot_proportions_by_course(
        df=my_dataframe,
        proportions_to_plot=['Proportion_Female', 'Proportion_Male'],
        pdf_filename='course_proportions.pdf',
        save_as_pdf=True
    )
"""
def plot_proportions_by_course(df, proportions_to_plot, pdf_filename=None, save_as_pdf=False):
    unique_courses = df['COURSE'].unique()
    unique_courses.sort()
    num_courses = len(unique_courses)

    if save_as_pdf and pdf_filename:
        pdf = PdfPages(pdf_filename)

    for proportion in proportions_to_plot:
        # Calculate the number of rows needed for the subplots
        num_rows = (num_courses - 1) // 3 + 1

        # Set up the figure and axes
        fig, axs = plt.subplots(num_rows, 3,
                                figsize=(20, 5 * num_rows))  # Adjusted the figsize based on the number of courses

        # If there's only one chart, it will not be in a 2D array format. This ensures that axs is always a 2D array.
        if num_courses == 1:
            axs = [axs]

        # Flatten the axes array for easy indexing
        axs_flat = axs.ravel()

        for idx, course in enumerate(unique_courses):
            course_df = df[df['COURSE'] == course]
            course_df = course_df.sort_values(by='Proportion_Total', ascending=False).head(10)

            # Calculate relative proportions for the proportion of interest
            proportion_height = course_df[proportion] * course_df['Proportion_Total']
            complement_height = (1 - course_df[proportion]) * course_df['Proportion_Total']

            # Stacked bar chart
            label = proportion.split("Proportion_")[1]
            axs_flat[idx].bar(course_df['major_matriculation'], proportion_height, label=label)
            axs_flat[idx].bar(course_df['major_matriculation'], complement_height, bottom=proportion_height)
            axs_flat[idx].set_title(course)
            axs_flat[idx].set_ylabel('Proportion')
            axs_flat[idx].set_xlabel('Major')
            axs_flat[idx].set_ylim(0, 0.8)
            axs_flat[idx].legend()

        # Hide any unused subplot axes
        for idx in range(num_courses, 3 * num_rows):
            axs_flat[idx].axis('off')

        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.9, wspace=0.2, hspace=0.3)
        plt.suptitle(proportion, fontsize=20)

        if save_as_pdf and pdf_filename:
            pdf.savefig(fig)  # saves the current figure into a pdf page
            plt.close(fig)  # close the figure to avoid too many open figures

        else:
            plt.show()  # display the figure

    if save_as_pdf and pdf_filename:
        pdf.close()
