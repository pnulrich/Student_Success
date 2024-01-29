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


#Determine the number of students who were retained in a major since the semester of matriculation
#major_code : 'BIO', 'CHM', etc
#years : four digit calendar year such as 2024
#ftfy : "first time first year" argument; when True, only those students with 0 transfer credits will be in the output
#2023-07-12 developed using ChatGPT 4.0 with Code Interpreter
def major_retention(student_df, major_code, years, ftfy = True):
    semester_codes = utilityfunctions.create_semesters(years)
    print(semester_codes)

    # Import the dataset
    working_df = student_df.copy()
    #working_df['Grad_term'] = working_df['Grad_term'].apply(utilityfunctions.adjust_grad_term)
    #semesters = list()

    #First time, first year argument ftfy defaults to True to in function. However, if we want to catch all students who matriculated in a time frame, the dataframe must not drop those with transfer credit
    if ftfy == False:
        working_df = working_df[
            (working_df['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
            (working_df['SDSTUMAIN_MAJOR'] == major_code) &
            (working_df['SDSTUMAIN_MATRIC_TERM'] == working_df['SDSTUDEMOG_TERM'])
            ]
        print(working_df)

    #If only FTFY students are desired (default behavior), dataframe should have 0 transfer hours
    else:
        working_df = working_df[
            (working_df['SDSTUMAIN_MATRIC_TERM'].isin(semester_codes)) &
            (working_df['SDSTUMAIN_MAJOR'] == major_code) &
            (working_df['SDSTUMAIN_MATRIC_TERM'] == working_df['SDSTUDEMOG_TERM']) &
            (working_df['SDSTUMAIN_TRANSFER_HOURS'].isna() | (
                    working_df['SDSTUMAIN_TRANSFER_HOURS'] == 0))
            ]
        print(working_df)


    # Compute the new column
    working_df['SDSTUMAIN_MATRIC_TERM'] = pd.to_datetime(working_df['SDSTUMAIN_MATRIC_TERM'], format='%Y%m')
    working_df['Grad_term'] = pd.to_datetime(working_df['Grad_term'], format='%Y%m')
    working_df['Grad_term_end'] = working_df['Grad_term'].apply(utilityfunctions.adjust_grad_term)
    working_df['Months_Between'] = (working_df['Grad_term_end'].dt.year - working_df[
        'SDSTUMAIN_MATRIC_TERM'].dt.year) * 12 + working_df['Grad_term_end'].dt.month - working_df[
                                       'SDSTUMAIN_MATRIC_TERM'].dt.month

    #Provide boolean flag to simplify various measures
    working_df['grad_flag'] = working_df['Grad_term'].notnull().astype(int)
    major_retention_flag = 'major_retention' + major_code
    working_df[major_retention_flag] = 0
    working_df.loc[(working_df['Grad_term'].notnull()) & (working_df['Major'] == major_code), major_retention_flag] = 1
    # Compute the summary statistics
    total_students = working_df.shape[0]
    non_graduates = working_df['Grad_term'].isna().sum()
    graduates = total_students - non_graduates
    major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)].shape[0]
    non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)].shape[0]


    #Compute time till graduation for different segments
    average_months_all = working_df['Months_Between'].mean()
    std_dev_months_all = working_df['Months_Between'].std()
    average_years_non_graduates = working_df[working_df['Grad_term'].isna()]['Months_Between'].mean()/12  # Should be NaN
    std_dev_years_non_graduates = working_df[working_df['Grad_term'].isna()]['Months_Between'].std()/12  # Should be NaN
    average_years_graduates = working_df[working_df['Grad_term'].notna()]['Months_Between'].mean()/12
    std_dev_years_graduates = working_df[working_df['Grad_term'].notna()]['Months_Between'].std()/12

    average_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)]['Months_Between'].mean() / 12
    std_dev_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)][
        'Months_Between'].std()/12

    average_years_non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)][
                                      'Months_Between'].mean() / 12
    std_dev_years_non_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] != major_code)][
                                      'Months_Between'].std() / 12

    #Compute institutional GPA at graduation for graduates in the specific major or different major

    #average_years_major_code_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == major_code)]['Months_Between'].mean() / 12
    #std_dev_years_bio_graduates = working_df[(working_df['Grad_term'].notna()) & (working_df['Major'] == 'BIO')][
    #                                  'Months_Between'].std() / 12

    #Need to pull in demog data from demographics of last semester because graduation purge report does not include GPA
    #gpa_all_graduates = working_df[(working_df['Grad_term'].notna())[]
    #gpa_bio_graduates =
    #gpa_non_bio_graduates

    # Create the summary DataFrame
    summary_df = pd.DataFrame(
        columns=['Category', 'Count', 'Percentage', 'Avg Years to Graduation', 'Std Dev Years to Graduation'])

    rows_list = [
        {'Category': 'Total Students', 'Count': total_students, 'Percentage': 100, 'Avg Years to Graduation': None,
         'Std Dev Years to Graduation': None},
        {'Category': 'Non-Graduates', 'Count': non_graduates, 'Percentage': non_graduates / total_students * 100,
         'Avg Years to Graduation': average_years_non_graduates,
         'Std Dev Years to Graduation': std_dev_years_non_graduates},
        {'Category': 'Graduates', 'Count': graduates, 'Percentage': graduates / total_students * 100,
         'Avg Years to Graduation': average_years_graduates, 'Std Dev Years to Graduation': std_dev_years_graduates},
        {'Category': 'Graduates Retained within Major', 'Count': major_code_graduates, 'Percentage': major_code_graduates / total_students * 100,
         'Avg Years to Graduation': average_years_major_code_graduates,
         'Std Dev Years to Graduation': std_dev_years_major_code_graduates},
        {'Category': 'Graduates who Left Major', 'Count': graduates - major_code_graduates,
         'Percentage': (graduates - major_code_graduates) / total_students * 100,
         'Avg Years to Graduation': average_years_non_major_code_graduates,
         'Std Dev Years to Graduation': std_dev_years_non_major_code_graduates}
    ]

    summary_df = pd.concat([summary_df, pd.DataFrame(rows_list)], ignore_index=True)

    # Return the result
    return(summary_df, working_df)

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
    working_df = demographics_df[demographics_df['Student_ID'].isin(student_ids)]

    # NOTE (2023-08-14) this analysis excludes those who earn two BS to keep things simple; not sure this is the best approach
    mask = working_df.duplicated(subset=['Student_ID', 'SDSTUDEMOG_TERM'], keep=False)  # Create a mask for duplicate rows where a student earns two degrees
    working_df = working_df[~mask]  # Apply the mask to keep only non-duplicate rows; that is, exclude those students who earned two BS
    #print(len(working_df))

    #loop through years and semesters to generate flags
    for academicyear in years:
        semesters = utilityfunctions.create_semesters([academicyear])

        # Filter to semesters associated with argument years
        df_filtered = working_df[working_df['SDSTUDEMOG_TERM'].isin(semesters)]
        #print(len(df_filtered))
        for student in student_ids:
            student_df = df_filtered[df_filtered['Student_ID'] == student]

            for semester in semesters:
                semester_df = student_df[student_df['SDSTUDEMOG_TERM'] == semester]

                if semester_df.empty:
                    continue

                #Flag non-graduated students as 0 and graduated students as 1
                #TO DO: Find a way for grad_flag to be set to 1 for the last semester of the degree rather than fixed characteristic
                if (semester_df[((semester_df['Student_ID'] == student) & (semester_df['Grad_term']) > 0)].empty):
                    grad_flag = 0
                else:
                    grad_flag = 1

                #indicate if student is still in the indicated major for this semester
                major_retention_flag = int((semester_df['SDSTUMAIN_MAJOR'] == major_code).all())
                major = semester_df['SDSTUMAIN_MAJOR'].item()
                grad_term = semester_df['Grad_term'].item()

                #add the semester and data for current student to the records list
                records.append({
                    'Student_ID': student,
                    'Semester': semester,
                    'AcademicYear': academicyear,
                    'major': major,
                    'major_retention_flag': major_retention_flag,
                    'grad_flag': grad_flag,
                    'grad_term': grad_term
                })

    #convert records to a single dataframe
    major_retention_df = pd.DataFrame(records)

    #for semesters of each academic year, calculate a running sum of how many semesters they were retained in major_code
    major_retention_df= major_retention_df.groupby('Student_ID').apply(calculate_running_retention_flag).reset_index(drop=True)

    #for students who changed major, it is helpful to know when they did this to determine where the curriculum structure could be affecting their decisions
    major_changed_df = major_retention_df[major_retention_df['major'] != major_code]  # create dataframe comprised of all students who changed to a different major
    major_changed_df = major_changed_df.reset_index(drop=True)  # reset index to ensure it is contiguous
    major_changed_df = major_changed_df.sort_values(by=['Semester'], ascending=True)
    idx = major_changed_df.groupby('Student_ID')['Semester'].idxmin()  # Find index of row with smallest 'Semester' for each 'Student_ID'
    major_changed_df = major_changed_df.loc[idx]
    major_changed_df.rename(columns={'Semester': 'major_change_semester'},inplace=True)  # rename the column to avoid confusion
    major_retention_df = pd.merge(major_retention_df, major_changed_df[['Student_ID', 'major_change_semester']], on='Student_ID', how = 'left', validate = 'many_to_one')

    # Determine how many semesters passed before student changed major
    # Group by 'Student_ID' and 'major_change_semester', then apply a lambda function to calculate the count
    semesters_before_major_change_df = (
        major_retention_df.groupby(['Student_ID', 'major_change_semester'])
        .apply(lambda x: (x['Semester'] < x['major_change_semester']).sum())
        .reset_index(name='semesters_before_major_change')
    )
    major_retention_df = pd.merge(major_retention_df, semesters_before_major_change_df, on=['Student_ID', 'major_change_semester'], how ='left')
    # major_retention_df['total_semesters'] = major_retention_df.groupby('Student_ID').size()
    major_retention_df['total_semesters'] = major_retention_df.groupby('Student_ID')['Student_ID'].transform('size')

    # Create a dataframe reportingt those who graduated that includes the last semester of their BS coursework
    grad_df = major_retention_df[(major_retention_df['grad_flag'] == 1)]  # creates a dataframe comprised of all students who graduated
    grad_df = grad_df.reset_index(drop=True)  # reset the index to ensure it is contiguous
    # grad_df['semesters_till_graduation'] = grad_df.groupby('Student_ID').size()
    idx_last_semester = grad_df.groupby('Student_ID')['Semester'].idxmax()  # Find the index of the row with the largest 'Semester' for each 'Student_ID'

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


    # demographics_df = pd.read_csv(
    #     r"C:\Research\Research Projects\GSU\HHMI_IE3\Analyses\Pilot_CalcCLS\Data_Compiled_Reference\S440270_GraduationPurge_Combined_20231030.csv")
    #
    # # Filter the demographics_df where 'SDSTUMAIN_MATRIC_TERM' == 'SDSTUDEMOG_TERM' and exclude the demographics_df rows for certificate data
    # equivalent_df  = demographics_df[
    #     (demographics_df['SDSTUMAIN_MATRIC_TERM'] == demographics_df['SDSTUDEMOG_TERM']) & (
    #                 demographics_df['Degree'] != 'CER0')]
    #
    # # 2. Filter records where SDSTUMAIN_MATRIC_TERM does not have a corresponding SDSTUDEMOG_TERM
    # non_equivalent_df = demographics_df[
    #     (demographics_df['SDSTUMAIN_MATRIC_TERM'] != demographics_df['SDSTUDEMOG_TERM']) &
    #     (demographics_df['Degree'] != 'CER0')
    #     ]
    #
    # # Find the earliest SDSTUDEMOG_TERM for each SDSTUMAIN_MATRIC_TERM in non_equivalent_df
    # earliest_terms = non_equivalent_df.groupby('SDSTUMAIN_MATRIC_TERM')['SDSTUDEMOG_TERM'].min().reset_index()
    #
    # # 2. Filter records where SDSTUMAIN_MATRIC_TERM does not have a corresponding SDSTUDEMOG_TERM for each Student_ID
    # non_equivalent_df = demographics_df[
    #     (demographics_df['SDSTUMAIN_MATRIC_TERM'] != demographics_df['SDSTUDEMOG_TERM']) &
    #     (demographics_df['Degree'] != 'CER0')
    #     ]
    #
    # # Group by Student_ID and get the earliest SDSTUDEMOG_TERM for each student
    # earliest_terms = non_equivalent_df.groupby('Student_ID')['SDSTUDEMOG_TERM'].min().reset_index()
    #
    # # Merge non_equivalent_df with earliest_terms to get the records
    # non_equivalent_df_filtered = pd.merge(non_equivalent_df, earliest_terms, on=['Student_ID', 'SDSTUDEMOG_TERM'])
    #
    # # Combine the two dataframes
    # filtered_demographics_df = pd.concat([equivalent_df, non_equivalent_df_filtered], axis=0)
    # print(len(filtered_demographics_df))

    # Convert 'grad_date' to datetime
    #filtered_demographics_df['Grad_date'] = pd.to_datetime(filtered_demographics_df['Grad_date'], format='%m/%d/%Y')
    input_demographics_df['Grad_date'] = pd.to_datetime(input_demographics_df['Grad_date'], format='%m/%d/%Y')

    # Find duplicate grad_dates
    #duplicate_dates = filtered_demographics_df[
    #    filtered_demographics_df.duplicated(subset=['Student_ID', 'Grad_date'], keep=False)]

    # Drop rows where 'Grad_date' is NaN or NaT for ease of review
    #duplicate_dates = duplicate_dates.dropna(subset=['Grad_date'])

    # Sort the DataFrame for better visualization
    #duplicate_dates.sort_values(by=['Student_ID', 'Grad_date'], inplace=True)

    # Print rows where 'grad_date' is equivalent; the vast majority of these represent situations where the first matriculation semester degree == '000'. When a student declares major,
    # this triggers another matriculation semester event associated with the newly declared major (e.g., 'CHM'). With my dataset, this occurs for 261 students and 538 demographics rows
   #print(duplicate_dates)

    # Sort by 'grad_date' and 'Student_ID'
    #filtered_demographics_df = filtered_demographics_df.sort_values(by=['Student_ID', 'Grad_date'])

    # Drop duplicate Student_ID rows, keeping the first (i.e., the one with the earliest grad_date)
    #filtered_demographics_df = filtered_demographics_df.drop_duplicates(subset='Student_ID', keep='first')

    # Merge the math_grades_df with the filtered demographics_df based on the Student_ID
    #merged_df = math_grades_df.merge(filtered_demographics_df, left_on='Student_ID', right_on='Student_ID', how='left')
    merged_df = math_grades_df.merge(input_demographics_df, left_on='Student_ID', right_on='Student_ID', how='left')
    #merged_df = institutionaldata.utilityfunctions.letter_grade_simplify(merged_df, c_minus_flag=1)

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

#2024-01-29 (PNU): This function is deprecated and replaced with course_sequence_analysis().
#2023-10-19 (PNU): uses data from combine_course_grades_with_demographics() to determine proportions of students who passed course
#course_name : string, name of course of interest (e.g., "CALC FOR THE LIFE SCIENCES I")
#df : dataframe containing grades and demographics
#major: string, code for major (e.g., "BIO")
#downstream_course: string, optional parameter for looking at movement to alternate course if DFW on first attempt
#node_pie: boolean; optional parameter that can be used to demonstrate population stats (like % female) for a specific node
def course_attempts_pydot(course_name, df, major, downstream_course=None, node_pie = False):
    # the following steps were worked out with ChatGPT4 as a way to avoid loss of students who switched their major after first attempt
    # whether or not this should be done is something to address in our research question. Are we interested in the downstream attempts to take the same course if they left the major?
    # Step 1: Get first attempts for all students for the course
    course_df_all_attempts = df[df['Reg_Crse_Title'] == course_name]
    course_df_all_attempts = course_df_all_attempts.sort_values(by=['Student_ID', 'Reg_Term'])
    course_df_first_attempts_all = course_df_all_attempts.drop_duplicates(subset=['Student_ID'], keep='first')

    # Step 2: Identify students with desired major in first attempt
    ############CAUTION: IS THIS THE CORRECT FILTERING? SHOULDN'T THIS BE FILTERED BY 'MAJOR' instead of 'Stu_Majr_Code1'?############
    desired_major_students = course_df_first_attempts_all[course_df_first_attempts_all['StuMajr_Code1'] == major]['Student_ID'].unique()
    ############CAUTION: IS THIS THE CORRECT FILTERING? SHOULDN'T THIS BE FILTERED BY 'MAJOR' instead of 'Stu_Majr_Code1'?############

    # Step 3: Filter all attempts for these students
    course_df = course_df_all_attempts[course_df_all_attempts['Student_ID'].isin(desired_major_students)]
    course_df_first_attempts = course_df.drop_duplicates(subset=['Student_ID'], keep='first')

    print(f"Results for {course_name}({len(course_df_first_attempts)} students):")
    # descriptives for the second attempts
    first_pass_number = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])])
    first_pass_proportion = len(
        course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])]) / len(
        course_df_first_attempts)
    first_DFW_number = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])])
    first_DFW_proportion = len(
        course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])]) / len(
        course_df_first_attempts)
    first_W_number = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['W'])])
    first_W_proportion = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['W'])]) / len(
        course_df_first_attempts)

    print(f"Proportion passing on first attempt: {round(first_pass_proportion, 2)} ({first_pass_number} students)")
    print(f"Proportion DFW on first attempt: {round(first_DFW_proportion, 2)} ({first_DFW_number} students)")
    print(f"Proportion W on first attempt: {round(first_W_proportion, 2)} ({first_W_number} students)")

    course_df_repeat_students = course_df[course_df.duplicated(subset=['Student_ID'], keep=False)]
    course_df_second_attempts = course_df_repeat_students[
        course_df_repeat_students.duplicated(subset=['Student_ID'], keep='first')]

    # descriptives for the second attempts
    proportion_DFW_repeat = len(course_df_second_attempts) / first_DFW_number
    second_pass_number = len(
        course_df_second_attempts[course_df_second_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])])
    second_pass_proportion = len(
        course_df_second_attempts[course_df_second_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])]) / len(
        course_df_second_attempts)
    second_DFW_number = len(
        course_df_second_attempts[course_df_second_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])])
    second_DFW_proportion = len(
        course_df_second_attempts[course_df_second_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])]) / len(
        course_df_second_attempts)
    # Find students who changed their major in the second attempt
    changed_major_second_attempt = course_df_second_attempts[course_df_second_attempts['StuMajr_Code1'] != major][
        'Student_ID'].nunique()

    print(f"\nNumber of second attempts: {len(course_df_second_attempts['Student_ID'].unique())}")
    print(f"Proportion passing on second attempt: {round(second_pass_proportion, 2)} ({second_pass_number})")
    print(f"Proportion DFW on second attempt: {round(second_DFW_proportion, 2)}  ({second_DFW_number})")
    print(f"\nNumber of students in the second attempt who changed major from {major}: {changed_major_second_attempt}")

    # If a downstream course is specified, check for switches to that course
    if downstream_course:
        # Step 4: Identify students who got a DFW on their first attempt for the main course
        dfw_students = course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])][
            'Student_ID'].unique()

        # Step 5: Check which of these students later switched to the downstream course
        switched_to_downstream = df[(df['Reg_Crse_Title'] == downstream_course) & df['Student_ID'].isin(dfw_students)][
            'Student_ID'].unique()

        print(
            f"\nNumber of students who got a DFW in {course_name} on the first attempt and later switched to '{downstream_course}': {len(switched_to_downstream)}")
    print("---------------------------")

    # Create a PyDot graph object
    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")

    # Create nodes for different categories
    first_attempt_proportion_female = len(course_df_first_attempts[course_df_first_attempts['SDSTUDEMOG_SEX'] == "F"]) / len(course_df_first_attempts)
    second_attempt_proportion_female = len(course_df_second_attempts[course_df_second_attempts['SDSTUDEMOG_SEX'] == "F"])/len(course_df_second_attempts)

    if(node_pie):
        first_attempt_node = pydot.Node("T1", shape="circle", style="wedged",
                                         fillcolor=f"blue;{first_attempt_proportion_female}:green")
        second_attempt_node = pydot.Node("T2", shape="circle", style ="wedged", fillcolor= f"blue;{second_attempt_proportion_female}:green")
    else:
        first_attempt_node = pydot.Node("T1", shape="box")
        second_attempt_node = pydot.Node("T2", shape="box")

    pass_first_attempt_node = pydot.Node("Pass (first attempt)", label="Pass")
    dfw_first_attempt_node = pydot.Node("DFW (first attempt)", label="DFW")
    dfw_no_repeat = pydot.Node("Did not repeat", label = "DN")
    pass_second_attempt_node = pydot.Node("Pass (second attempt)", label="Pass")
    dfw_second_attempt_node = pydot.Node("DFW (second attempt)", label="DFW")


    # Add nodes to the graph
    graph.add_node(first_attempt_node)
    graph.add_node(second_attempt_node)
    graph.add_node(pass_first_attempt_node)
    graph.add_node(dfw_first_attempt_node)
    graph.add_node(dfw_no_repeat)
    graph.add_node(pass_second_attempt_node)
    graph.add_node(dfw_second_attempt_node)

    # Create edges and set labels
    first_pass_label = f"{round(first_pass_proportion, 2)} ({first_pass_number})"
    dfw_first_attempt_label = f"{round(first_DFW_proportion, 2)} ({first_DFW_number})"
    proportion_DFW_repeat_label = f"{round(proportion_DFW_repeat, 2)} ({len(course_df_second_attempts)})"
    proportion_DFW_no_repeat_label = f"{round(1-proportion_DFW_repeat, 2)} ({first_DFW_number-len(course_df_second_attempts)})"
    second_pass_label = f"{round(second_pass_proportion, 2)} ({second_pass_number})"
    second_DFW_label = f"{round(second_DFW_proportion, 2)} ({second_DFW_number})"

    # Define a list of edge descriptions as tuples
    edges_data = [
        (first_attempt_node, pass_first_attempt_node, first_pass_label),
        (first_attempt_node, dfw_first_attempt_node, dfw_first_attempt_label),
        (dfw_first_attempt_node, dfw_no_repeat, proportion_DFW_no_repeat_label),
        (dfw_first_attempt_node, second_attempt_node, proportion_DFW_repeat_label),
        (second_attempt_node, pass_second_attempt_node, second_pass_label),
        (second_attempt_node, dfw_second_attempt_node, second_DFW_label)
    ]

    # Create edges with labels using a loop through the edges_data tuple
    for source, target, label in edges_data:
        edge = pydot.Edge(source, target, label=label)
        graph.add_edge(edge)

    # If a downstream course is specified, add related nodes and edges
    if downstream_course:
        # Add nodes and edges for downstream course
        downstream_course_node = pydot.Node(downstream_course, shape="box")
        graph.add_node(downstream_course_node)
        switched_to_downstream_label = f"Switched to {downstream_course}"

        # Create the edge without setting the label argument
        edge = pydot.Edge(dfw_first_attempt_node, downstream_course_node)
        # Set the label attribute for the edge
        edge.set_label(switched_to_downstream_label)

        graph.add_edge(edge)
    # Set graph attributes
    graph.set("nodesep", "0.3")  # Adjust as needed
    # Save or render the graph
    image_filename = f"{course_name}_attempts_graph.png"
    graph.write_png(image_filename)


    # Create a figure and show the saved image using Matplotlib
    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Course Attempts for {major} majors in {course_name}", fontsize = 16)

    fig.tight_layout()
    ax = fig.add_subplot(111)  # 1 row, 1 column, 1st subplot
    ax.axis('off')
    # Define the portion of the figure to fill
    left, bottom, width, height = 0.15, 0.15, 0.7, 0.7  # Adjust these values as needed

    # Create the subplot within the defined portion
    ax.set_position([left, bottom, width, height])

    # Load and display the saved image using Matplotlib
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()


#2023-10-27 Modified base code with ChatGPT4.0 to create subsequent course analysis work
#this is likely not a necessary extra function and only has minor returning differences
#2024-01-19 Revised and improved calculations because proportions of retakes were incorrect; used lots print statements to follow calculations
def analyze_course(course_name, df, major, prerequisite_course = False, node_pie = False):
    # Check if DataFrame is empty
    if df.empty:
        print("DataFrame is empty.")
        return None

    print(len(df))
    # Step 1: Get all attempts for the course
    course_df_all_attempts = df[(df['Reg_Crse_Title'] == course_name)]  # the reason we don't filter by major yet is because students in major at first attempt may switch to another major later
    course_df_all_attempts = course_df_all_attempts.sort_values(by=['Student_ID', 'Reg_Term'], ascending=[True, True])
    print(f"Total attempts for {course_name}: {len(course_df_all_attempts)}")
    # course_df_all_attempts = df[(df['Reg_Crse_Title'] == course_name) & (df['Major'] == major)]

    # print(f"Total attempts for {major} majors in {course_name}: {len(course_df_all_attempts)}")

    # Check if there are no attempts for the course
    if course_df_all_attempts.empty:
        print(f"No attempts found for {course_name}.")
        return None

    # print(list(course_df_all_attempts))
    course_df_first_attempts_all = course_df_all_attempts.drop_duplicates(subset=['Student_ID'], keep='first')
    print(f"Number of unique students in first attempt of {course_name}: {len(course_df_first_attempts_all)}")


    # Step 2: Identify students with desired major in first attempt
    desired_major_students = course_df_first_attempts_all[(course_df_first_attempts_all['Major'] == major)]['Student_ID'].unique()
    #return desired_major_students
    print(f"Number of unique {major} majors  : {len(desired_major_students)}")

    # Step 3: Filter all attempts for these students
    course_df = course_df_all_attempts[course_df_all_attempts['Student_ID'].isin(desired_major_students)]
    course_df_first_attempts = course_df.drop_duplicates(subset=['Student_ID'], keep='first')
    #print(len(course_df_first_attempts))
    #print(len(course_df_first_attempts['Student_ID'].unique())) # # of Student_ID matches number of lines; no duplications

    # Descriptives for the first attempts
    first_pass_number = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])])
    first_pass_proportion = first_pass_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0
    first_DFW_students = course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])]['Student_ID'].unique()
    first_DFW_number = len(course_df_first_attempts[course_df_first_attempts['Final_GRDE_Simp'].isin(['D', 'F', 'W'])])
    # WE ARE MISSING 1 OF THE 2781 BIO majors in first attempt; 745+ 2035 = 2780; There is an "N" grade value in the dataset (this is a continuing education student who needs to be filtered out)
    # print(course_df_first_attempts['Final_GRDE_Simp'].unique())
    # print(first_pass_number)
    # print(first_pass_proportion)
    # print(first_DFW_number)
    first_DFW_proportion = first_DFW_number / len(course_df_first_attempts) if len(course_df_first_attempts) > 0 else 0
    # print(first_DFW_proportion)

    # Repeat analysis for students who did not pass the first time
    course_df_repeat_attempts_all = course_df[course_df.duplicated(subset=['Student_ID'], keep=False)]
    # print(len(course_df_repeat_attempts_all))
    # print(len(course_df_repeat_attempts_all['Student_ID'].unique()))
    course_df_second_attempts = course_df_repeat_attempts_all[course_df_repeat_attempts_all.duplicated(subset=['Student_ID'], keep='first')]
    second_attempt_number = len(course_df_second_attempts)
    # print(len(course_df_second_attempts))
    # Descriptives for the second attempts
    proportion_DFW_repeat = len(course_df_second_attempts) / first_DFW_number if first_DFW_number > 0 else 0
    # print(proportion_DFW_repeat)

    second_pass_number = len(course_df_second_attempts[course_df_second_attempts['Final_GRDE_Simp'].isin(['A', 'B', 'C'])])
    #print(second_pass_number)
    second_pass_proportion = second_pass_number / len(course_df_second_attempts) if len(course_df_second_attempts) > 0 else 0
    #print(second_pass_proportion)
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
        "second_pass_proportion": second_pass_proportion
    }

    # Use block below to trouble-shoot disparities in numbers in prereq vs numbers in downstream course
    # if prerequisite_course:
    #    print(len(course_df_all_attempts[(course_df_all_attempts['Major'] == 'CHM') &(course_df_all_attempts['Reg_Crse_Title'] == prerequisite_course)]))
    #    print(len(course_df_all_attempts[course_df_all_attempts['Major'] == 'CHM']['Student_ID'].unique()))

    return descriptives, df[df['Major'] == 'CHM']

#2023-10-28 Paul Ulrich, generated with ChatGPT4.0
def calculate_alternate_entry(course_name, df, major, prerequisite_course = False):
    # Get students who are in the course but not in the prerequisite course
    students_in_course = df[(df['Reg_Crse_Title'] == course_name) & (df['Major'] == major)]['Student_ID'].unique()
    #print(students_in_course)
    print(f"Number of unique students in course {course_name}: ", len(students_in_course))

    if prerequisite_course:
        #print(df['Reg_Crse_Title'].unique())
        students_in_prerequisite = set(df[df['Reg_Crse_Title'] == prerequisite_course]['Student_ID'].unique())
        #print(students_in_prerequisite)
        print(f"Number of unique students in prerequisite {prerequisite_course}: ", len(students_in_prerequisite))
        alternate_entry_students = [student for student in students_in_course if student not in students_in_prerequisite]
        #print(alternate_entry_students)
        print("Alternate entry students : ", len(alternate_entry_students))

    # Calculate proportion and number
    #proportion_alternate_entry = len(alternate_entry_students) / len(students_in_course) if len(students_in_course) > 0 else 0
    number_alternate_entry = len(alternate_entry_students)

    return number_alternate_entry

#2023-10-28 Paul Ulrich, generated with ChatGPT4.0
# 2024-01-19 Paul Ulrich, updated with corrected filtering
def calculate_not_taking_next(current_course, next_course, df, major):
    # Step 1: Get students who passed the current course
    passed_students = df[(df['Reg_Crse_Title'] == current_course) & (df['Final_GRDE_Simp'].isin(['A', 'B', 'C'])) & (df['Major'] == major)]['Student_ID'].unique()
    #print("Passed students for ", current_course, " : \n")
    #print(passed_students) # use this line to trouble-shoot odd situations where students didn't pass or didn't have prereq
    print("Number of passed students : ", len(passed_students))
    # Step 2: Check how many of these students did not take the next course
    did_not_take_next = [student for student in passed_students if student not in df[(df['Reg_Crse_Title'] == next_course) & (df['Major'] == major)]['Student_ID'].unique()]
    did_take_next = [student for student in passed_students if student in df[(df['Reg_Crse_Title'] == next_course) & (df['Major'] == major)]['Student_ID'].unique()]
    print('Number of passed students who did take the next course : ', len(did_take_next))
    #print('Did take next : \n', did_take_next) # use this line to trouble-shoot odd situations where students didn't pass or didn't have prereq
    # Step 3: Calculate proportion and number
    proportion_not_taking_next = len(did_not_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_not_taking_next = len(did_not_take_next)
    proportion_taking_next = len(did_take_next) / len(passed_students) if len(passed_students) > 0 else 0
    number_taking_next = len(did_take_next)
    print("Number of passed students who did not take the next course : ", number_not_taking_next)
    print("Proportion of passed students who did not take the next course : ", proportion_not_taking_next)
    return proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next

#2023-10-28 (PNU, modified as extension from course_attempts_pydot() with ChatGPT4.0):
#uses data from combine_course_grades_with_demographics() to determine proportions of students who passed course
#course_sequence : list of strings representing names of courses of interest (e.g., "CALC FOR THE LIFE SCIENCES I")
#df : dataframe containing grades and demographics
#major: string, code for major (e.g., "BIO")
# [not implemented yet] node_pie: boolean; optional parameter that can be used to demonstrate population stats (like % female) for a specific node
def course_sequence_analysis(course_sequence, df, major, node_pie = False):
    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    next_course_name = course_sequence[1]
    previous_pass_node = None
    for index, course_name in enumerate(course_sequence):
        # Analyze the course
        if index == 0:
            #print('Courses in non prereq loop : ', df['Reg_Crse_Title'].unique())
            descriptives, data = analyze_course(course_name, df, major)

        if index > 0:
            #print('Courses in prereq loop : ', df['Reg_Crse_Title'].unique())
            descriptives, data = analyze_course(course_name, df, major, course_sequence[index-1])

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

        # Create edges and set labels with limited significant figures
        graph.add_edge(pydot.Edge(course_node, pass_node, label=f"{descriptives['first_pass_proportion']:.3f} ({descriptives['first_pass_number']})"))
        graph.add_edge(pydot.Edge(course_node, dfw_node, label=f"{descriptives['first_DFW_proportion']:.3f} ({descriptives['first_DFW_number']})"))
        graph.add_edge(pydot.Edge(dfw_node, retake_node, label=f"{descriptives['proportion_DFW_repeat']:.3f} ({descriptives['second_attempt_number']})"))
        if index < len(course_sequence) - 1:
            graph.add_edge(pydot.Edge(dfw_node, did_not_take_next_node, label=f"{1-descriptives['proportion_DFW_repeat']:.3f}"))
        graph.add_edge(pydot.Edge(retake_node, pass_node, label=f"{descriptives['second_pass_proportion']:.3f} ({descriptives['second_pass_number']})"))

        #if index < len(course_sequence):
        #    graph.add_edge(pydot.Edge(retake_node, did_not_take_next_node,label=f"{1-descriptives['second_pass_proportion']:.3f}"))

        # Edge for students who pass but do not take the next course
        if index < len(course_sequence) - 1:
            next_course_name = course_sequence[index + 1]
            #print(next_course_name)
            proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next = calculate_not_taking_next(
                course_name, next_course_name, df, major)
            graph.add_edge(pydot.Edge(pass_node, did_not_take_next_node, label=f"{proportion_not_taking_next:.3f} ({number_not_taking_next})"))

        # Node and edge for students entering from an alternate pathway
        if index > 0:
            prerequisite_course_name = course_sequence[index - 1]
            #number_alternate_entry = calculate_alternate_entry(course_name, df, major, prerequisite_course_name)
            number_alternate_entry = calculate_alternate_entry(course_name, data, major, prerequisite_course_name)
            alternate_entry_node = pydot.Node(f"Alternate Entry to {course_name}", label="Alternate Entry")
            graph.add_node(alternate_entry_node)
            graph.add_edge(pydot.Edge(alternate_entry_node, course_node, label=f"{number_alternate_entry}"))

        if index > 0:
            prerequisite_course_name = course_sequence[index - 1]
            print('Prerequisite for : ', course_name, ' is ', prerequisite_course_name)
            proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next = calculate_not_taking_next(
                prerequisite_course_name, course_name, df, major)
            graph.add_edge(pydot.Edge(previous_pass_node, course_node,
                                      label=f"{proportion_taking_next:.3f} ({number_taking_next})"))

        previous_pass_node = pass_node

    # Set graph attributes
    graph.set("nodesep", "1.0")

    # Save or render the graph
    image_filename = "course_sequence_attempts_graph.png"
    graph.write_png(image_filename)

    # Display the graph
    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Course Sequence Analysis for {major} Majors", fontsize=16)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()


#2023-11-01 (Paul Ulrich/ChatGPT4)
def track_major_change(initial_df, demographics_df, range_first_term_start = 200501, range_first_term_stop = 203001, matric_term_earliest = 200501, initial_major='BIO'):
    """
    Track students who started with a specified major and then changed
    to another specified major by the fall of their 3rd year.

    Args:
    - initial_df (pd.DataFrame): DataFrame containing demographics from first semester students took classes.
    - demographics_df (pd.DataFrame): Larger DataFrame containing demographics for all semester data.
    - initial_major (str): The major to track initially.
    - range_first_term_stop (int): term code (YYYYMM) representing the last semester a student could have started courses
    - range_first_term_start (int): term code (YYYYMM) representing the first semester of interest a student could have started courses
`   - matric_term_earliest (int): term code (YYYYMM) representing the earliest matriculation term that will be included in the dataset
    Returns:
    - pd.DataFrame: DataFrame with students' initial major,  major in fall of 3rd year, graduation status, sex, race, ethnicity, birth year, and GPA at first semester.
    """

    # Filter for students with the specified initial major
    filtered_initial_df = initial_df[(initial_df['SDSTUMAIN_MAJOR'] == initial_major) & (initial_df['SDSTUDEMOG_TERM'] <= range_first_term_stop) &(initial_df['SDSTUDEMOG_TERM'] >= range_first_term_start) & (initial_df['SDSTUMAIN_MATRIC_TERM'] >= matric_term_earliest)].copy()

    # Calculate the expected term for the fall of the 3rd year
    filtered_initial_df['Year'] = filtered_initial_df['SDSTUDEMOG_TERM'] // 100
    filtered_initial_df['ThirdYearFallTerm'] = (filtered_initial_df['Year'] + 2) * 100 + 8

    # Use this term and Student_ID to filter the larger demographics_df
    third_year_df = demographics_df[demographics_df.set_index(['Student_ID', 'SDSTUDEMOG_TERM']).index.isin(
        filtered_initial_df.set_index(['Student_ID', 'ThirdYearFallTerm']).index)]

    # Merge initial_df with third_year_df
    result_df = filtered_initial_df.merge(third_year_df, on='Student_ID', suffixes=('', '_3rdYear'), how = "left")

    # Identify students who don't have a third-year entry
    missing_third_year = result_df['SDSTUMAIN_MAJOR_3rdYear'].isna()
    missing_count = missing_third_year.sum()
    print(f"{missing_count} students don't have a corresponding demographic entry for Fall of their third year.")

    return result_df[['SDSTUDEMOG_TERM', 'Student_ID', 'BirthYear', 'SDSTUDEMOG_ETHNICITY_CODE', 'SDSTUDEMOG_RACE', 'SDSTUDEMOG_SEX','SDSTUMAIN_MAJOR', 'SDSTUGPA_GPA_INST', 'SDSTUMAIN_MATRIC_TERM', 'SDSTUMAIN_MAJOR_3rdYear', 'Grad_year', 'Grad_term', 'Degree']]

#2023-11-29 modification from (2023-11-24 prototype with initial guidance from ChatGPT4 for major retention) to extend to leaving by 3rd year
#df_demographics: pandas dataframe holding demographics for first semester
#df_math_grades: pandas dataframe with course scores for courses of interest
#df_hsgpa: pandas dataframe comprised of high school GPA of students
#reference_course: course which GLM will benchmark against as baseline; default is precalculus
#left : defaults to 0, indicating that analysis will be about retention in major; 1, determine predictors for those who left
def glm_retention_analysis(df_demographics, df_math_grades, df_hsgpa, reference_course='PRECALCULUS', left = 0):
    if(len(df_demographics['SDSTUMAIN_MAJOR'].unique())>1):
        print("CAUTION: This function only accepts data for a single major. Your dataset included the following majors: ", df_demographics['SDSTUMAIN_MAJOR'].unique())
        return

    # convert 'SDSTUDEMOG_SEX' data  to categorical where 'F' = 1 and 'M' = 0
    df_demographics['SDSTUDEMOG_SEX'] = df_demographics['SDSTUDEMOG_SEX'].replace(
        {'F': 1, 'M': 0}).astype(int)
    print("Length of major_demographics_df input = ", len(df_demographics), " and number of unique students = ",
          len(df_demographics['Student_ID'].unique()))

    # Merge with math grades using the earliest math course record for each student
    mask = df_math_grades.groupby('Student_ID')['Reg_Term'].idxmin()
    first_math_course_df = df_math_grades.loc[mask]
    merged_df = df_demographics.merge(first_math_course_df, on='Student_ID', how='left')
    merged_df = merged_df[~(merged_df['SDSTUDEMOG_TERM'] > merged_df['Reg_Term'])]

    print("Length of merged_df after merge with first_math_course_df = ", len(merged_df),
          " and number of unique students = ",
          len(merged_df['Student_ID'].unique()))
    # Merge with high school GPA information
    merged_df = merged_df.merge(df_hsgpa[['Student_ID', 'HS_AVERAGE']], on='Student_ID', how='left')

    # duplicated_df = merged_df[merged_df[['Student_ID', 'HS_AVERAGE']].duplicated(keep = False)]
    # print(len(duplicated_df))
    print("Length of merged_df after merge with df_hsgpa = ", len(merged_df), " and number of unique students = ",
          len(merged_df['Student_ID'].unique()))
    # merged_df = merged_df[~merged_df[['Student_ID', 'HS_AVERAGE']].duplicated(keep='first')]
    merged_df = merged_df[~merged_df.duplicated(subset=['Student_ID', 'HS_AVERAGE'], keep='first')]

    # merged_df = merged_df[~merged_df['HS_AVERAGE_y'].isnull()]
    print("Length of merged_df after merge with df_hsgpa and removal of duplicates = ", len(merged_df),
          " and number of unique students = ", len(merged_df['Student_ID'].unique()))

    # Create flags for major retention by the 3rd year and if the student left
    merged_df['Major_Retention_3rdYear'] = (
                merged_df['SDSTUMAIN_MAJOR_3rdYear'] == merged_df['SDSTUMAIN_MAJOR']).astype(int)
    merged_df['left_by_3rdYear_flag'] = merged_df['SDSTUMAIN_MAJOR_3rdYear'].isnull().astype(int)

    # Calculate number of months from start of first semester to the start of the semester of first math course
    merged_df['Months_Difference'] = ((merged_df['Reg_Term'] // 100 - merged_df[
        'SDSTUDEMOG_TERM'] // 100) * 12) + (merged_df['Reg_Term'] % 100 - merged_df['SDSTUDEMOG_TERM'] % 100)

    # Exclude students who never took one of the math courses
    merged_df = merged_df[~merged_df['Months_Difference'].isnull()]
    print("After excluding those who never took a math course ", len(merged_df))

    # Drop rows without high school GPA data or who left by 3rd year
    merged_df = merged_df.dropna(subset=['HS_AVERAGE'])
    print("After excluding those who don't have a HS GPA: ", len(merged_df))

    # Exclude honor courses
    merged_df = merged_df[~merged_df['Reg_Crse_Title'].str.contains(r'\bhon\b', case=False, na=False)]
    print("After excluding students in honors sections: ", len(merged_df))

    # if we are interested in retention in the major at 3rd year, run GLM with 'Major_Retention_3rdYear' as response variable
    if(left == 0):
        remained_df = merged_df[merged_df['left_by_3rdYear_flag'] == 0]
        print("After excluding those who left by 3rd year: ", len(remained_df))

        # Generate dummy variables for course titles excluding the reference course
        course_title_dummies = pd.get_dummies(remained_df['Reg_Crse_Title'], prefix='Course')
        course_title_dummies.drop(f'Course_{reference_course}', axis=1, inplace=True)

        # Prepare the final DataFrame for GLM
        X = remained_df[['SDSTUDEMOG_SEX','SDSTUGPA_GPA_INST','Months_Difference', 'HS_AVERAGE']].join(course_title_dummies)

        # Convert boolean columns to 'int64' if any
        X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})

        # Drop the 'Reg_Crse_Title' column if it's still present
        if 'Reg_Crse_Title' in X.columns:
            X = X.drop('Reg_Crse_Title', axis=1)

        y = remained_df['Major_Retention_3rdYear']

        # Fit the GLM
        model = sm.GLM(y, X, family=sm.families.Binomial())
        results_GLM = model.fit()
        return results_GLM

    #if we are interested in predictors of students leaving the university,run the GLM with 'left_by_3rdYear_flag' as response variable
    if (left == 1):
        left_df = merged_df

        # Generate dummy variables for course titles excluding the reference course
        course_title_dummies = pd.get_dummies(left_df['Reg_Crse_Title'], prefix='Course')
        course_title_dummies.drop(f'Course_{reference_course}', axis=1, inplace=True)

        # Prepare the final DataFrame for GLM
        X = left_df[['SDSTUDEMOG_SEX', 'SDSTUGPA_GPA_INST', 'Months_Difference', 'HS_AVERAGE']].join(
            course_title_dummies)

        # Convert boolean columns to 'int64' if any
        X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})

        # Drop the 'Reg_Crse_Title' column if it's still present
        if 'Reg_Crse_Title' in X.columns:
            X = X.drop('Reg_Crse_Title', axis=1)

        y = left_df['left_by_3rdYear_flag']

        # Fit the GLM
        model = sm.GLM(y, X, family=sm.families.Binomial())
        results_GLM = model.fit()
        return results_GLM

# Example usage:
# Assuming you have the required data in the three dataframes: demographics_df, math_grades_df, hsgpa_df
# result = glm_major_retention_analysis(demographics_df, math_grades_df, hsgpa_df, major='BIO', reference_course='PRECALCULUS', left = 0)
# print(result.summary())

#2024-01-05 creates box and whisker plots for performance in a course by the attempt in the class
#NOTE: withdrawals are not included
#data: pandas dataframe holding grades data
#course_prefix: string; department code for course of interest; e.g., MATH
#course_number: integer; numeric code for course of interest, e.g., 1111
#max_attempts: integer; largest number of attempts of a course that we are interested in
#return_results: default = 0, no return value; 1 = return a dataframe comprised of all student ID's attempt #, and numeric grade
def plot_attempt_descriptive_stats(data, course_prefix, course_number, max_attempts=4, return_results=0):
    # Filter the data to include only the specified course number and exclude withdrawals (coded as -1) that would skew results
    course_data = data[
        (data['COURSE_PREFIX'] == course_prefix) & (data['COURSE_NUMBER'] == course_number) & (data['Num_GRDE'] != -1)]
    course_data = course_data.sort_values(by=['Student_ID', 'TERM'], ascending=[True, True])

    # Initialize an empty list to store the sorted data
    data_list = []

    # Group the data by 'Student_ID'
    grouped_data = course_data.groupby('Student_ID')

    # Initialize lists to store descriptive statistics for each attempt
    descriptive_stats_list = [[] for _ in range(max_attempts)]

    # Loop through grouped data to calculate and store descriptive statistics for each attempt
    for student_id, group in grouped_data:
        for attempt in range(1, max_attempts + 1):
            if len(group) >= attempt:
                attempt_data = group.iloc[attempt - 1]
                descriptive_stats_list[attempt - 1].append(attempt_data['Num_GRDE'])
                if return_results:
                    data_list.append([student_id, attempt, attempt_data['Num_GRDE']])

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
    columns = ['Student_ID', 'Attempt', 'Num_GRDE']

    # send back data
    if return_results:
        return pd.DataFrame(data_list, columns=columns)

# Example usage:
# Call the function with the DataFrame and specify the course number and maximum attempts
# plot_attempt_descriptive_stats(math_1111_1113, course_prefix = 'MATH', course_number=1111, max_attempts=3, return_results = 1)

def process_math_chem_data(input_df, course_prefix, course_number):
    course_number = int(course_number)
    # Drop rows with 'LETTER_GRADE' == 'nan'
    input_df = input_df[~(input_df['LETTER_GRADE'] == 'nan')]

    # Remove duplicate rows
    input_df = input_df[~input_df.duplicated(
        subset=['Student_ID', 'TERM', 'COURSE_PREFIX', 'COURSE_SUFFIX', 'COURSE_NUMBER', 'LETTER_GRADE'],
        keep='first')]

    # Create 'flag_course_PC' column
    input_df['flag_course_PC'] = (input_df['COURSE_COLLEGE'] == 'PC').astype(int)

    nonK_df = input_df[(input_df['COURSE_PREFIX'] == course_prefix) &
                                (input_df['COURSE_NUMBER'] == course_number) &
                                (input_df['flag_course_PC'] == 1)]  # this captures ALL rows of CHEM 1211 that were taken as lab or lecture components at Perimeter College

    print("Rows in non-K course number = ", len(nonK_df))

    # Filter rows for the specified course_prefix and course_number
    course_df = input_df[(input_df['COURSE_PREFIX'] == course_prefix) &
                         (input_df['COURSE_NUMBER'] == course_number)]


    ##############################################################################################
    #2024-01-17 SMALL DISPARITIES IN PRIOR FILTERING OCCUR SOMEWHERE IN THIS EARLIEST TERMS LOGIC
    ##############################################################################################

    # Find the earliest 'TERM' for each 'Student_ID' for the specified course
    earliest_terms_nonK = nonK_df.groupby('Student_ID')['TERM'].min().reset_index()

    # Filter rows for the specified course_prefix and course_number with suffix 'K'
    course_k_df = input_df[(input_df['COURSE_PREFIX'] == course_prefix) &
                           (input_df['COURSE_NUMBER'] == course_number) &
                           (input_df['COURSE_SUFFIX'] == 'K')]

    print("Rows in K course number = ", len(course_k_df))

    # Find the earliest 'TERM' for each 'Student_ID' for the specified course with suffix 'K'
    earliest_terms_k = course_k_df.groupby('Student_ID')['TERM'].min().reset_index()

    # Merge the earliest 'TERM' values for both the specified course and course with suffix 'K'
    merged_terms = pd.merge(earliest_terms_k, earliest_terms_nonK, on='Student_ID', how='left')
    #print(list(merged_terms))
    #print(merged_terms)

    # Filter out rows where 'TERM_x' is later than 'TERM_y' for the specified course with suffix 'K'
    filtered_result_df = merged_terms[merged_terms['TERM_x'] <= merged_terms['TERM_y']]
    #print(list(filtered_result_df))
    #print(merged_terms)

    print("Number of students before exclusion of those who took it before : ", len(course_k_df))
    # Exclude students who took the specified course before
    course_k_df = course_k_df[~course_k_df['Student_ID'].isin(filtered_result_df['Student_ID'])]
    print("Number of students after exclusion of those who took it before : ", len(course_k_df))

    # Initialize a list to store values for a first attempt of the course
    flag_first_attempt = []

    # Group the data by 'Student_ID'
    grouped_data = course_k_df.groupby('Student_ID')

    # Calculate the minimum 'TERM' value for the specified course for each student
    min_term_by_student = grouped_data.apply(lambda group: group[group['COURSE_NUMBER'] == course_number]['TERM'].min())

    # Create a flag column based on the minimum 'TERM' value
    course_k_df[f'flag_first_attempt_{course_prefix}_{course_number}'] = (
        course_k_df.groupby('Student_ID')['TERM']
        .transform(lambda x: x == min_term_by_student[x.name]).astype(int))

    # Define a list of math course numbers for which you want to create flags
    math_course_numbers = [1111, 1113, 2201, 2202, 2211, 2212]

    # Create a DataFrame to store the math course data for all students
    math_courses_df = input_df[input_df['COURSE_NUMBER'].isin(math_course_numbers)]

    # Merge the math course data with the specified course with suffix 'K' on 'Student_ID' and 'TERM' using a left join
    merged_df = pd.merge(course_k_df, math_courses_df, on=['Student_ID', 'TERM'], how='left')

    print("Number of non-first attempts : ", len(merged_df[merged_df[f'flag_first_attempt_{course_prefix}_{course_number}'] == 0]))
    print("Number of first attempts : ", merged_df[f'flag_first_attempt_{course_prefix}_{course_number}'].sum())

    # Iterate over math course numbers to create flags
    for math_course in math_course_numbers:
        # Define a new column name for the flag
        flag_column_name = f'flag_MATH{math_course}'

        merged_df[flag_column_name] = 0

        # Create a boolean mask for students who took the specific math course during the same term they took the specified course with suffix 'K'
        mask = (merged_df['COURSE_NUMBER_y'] == math_course)

        # Set the flag to 1 for rows that satisfy the condition
        merged_df.loc[mask, flag_column_name] = 1

    # Filter merged_df to keep only the rows where 'Student_ID' appears once
    duplicate_students = merged_df[merged_df.duplicated(subset=['TERM', 'Student_ID'])]['Student_ID']
    filtered_merged_df = merged_df[~merged_df['Student_ID'].isin(duplicate_students)]

    print("Total number of students in filtered_merged_df after dropping of those from merged_df with duplicate 'TERM' and 'Student_ID : ",
        len(filtered_merged_df))

    # Filter rows with non-first attempts and negative 'Num_GRDE' values
    first_attempt_df = filtered_merged_df[filtered_merged_df[f'flag_first_attempt_{course_prefix}_{course_number}'] == 1].copy()
    first_attempt_df = first_attempt_df[~(first_attempt_df['Num_GRDE_x'] < 0)]
    print(len(first_attempt_df))

    print("Total number of first attempts before exclusion of those without SORHSCH_GPA or Num_GRDE values = ", len(first_attempt_df))

    # Check if 'SEX_x' is present in the DataFrame
    if 'SEX_x' not in first_attempt_df.columns:
        raise KeyError('SEX_x column is missing from the DataFrame')

    # Convert categorical variables to dummy variables
    first_attempt_df = pd.get_dummies(first_attempt_df, columns=['SEX_x'], drop_first=True)

    # Create a list of predictor columns
    predictor_columns = ['SEX_x_M']+[f'flag_MATH{math_course}' for math_course in math_course_numbers]

    # Check if the predictors are all in the DataFrame
    missing_predictors = [col for col in predictor_columns if col not in first_attempt_df.columns]
    if missing_predictors:
        raise KeyError(f'The following predictor columns are missing from the DataFrame: {missing_predictors}')

    # Add a constant to the model (intercept)
    X = sm.add_constant(first_attempt_df[predictor_columns])
    X = X.astype({col: 'int64' for col in X.select_dtypes(include=['bool']).columns})

    # Set up the y for the GLM
    y = first_attempt_df['Num_GRDE_x']

    # Fit the GLM
    model = sm.GLM(y, X, family=sm.families.Gaussian())
    results_GLM = model.fit()

    # Dictionary to hold the sample sizes for each math course
    sample_sizes = {}

    for math_course in math_course_numbers:
        flag_column = f'flag_MATH{math_course}'
        # Sum up the flag column to get the number of students who took the specified math course along with the specified course with suffix 'K'
        sample_sizes[f'MATH{math_course}'] = first_attempt_df[flag_column].sum()

    # Print results and sample sizes
    print(results_GLM.summary(), "\n\n Sample Sizes for each course:", sample_sizes)

    # Finally, return the processed DataFrame
    return first_attempt_df
