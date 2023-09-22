import pandas as pd
#import institutionaldata.utilityfunctions
import numpy as np

import institutionaldata.utilityfunctions
import institutionaldata.utilityfunctions as utilityfunctions
import matplotlib.pyplot as plt
from tabulate import tabulate
from tkinter import filedialog as fd
import tkinter as tk

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
    math_grades_df_copy['Final_GRDE_Simp'] = utilityfunctions.letter_grade_simplify(math_grades_df_copy)['Final_GRDE_Simp']

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
    major_code_student_ids = major_code_df['StudentID'].unique()
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
            (demographics_df_copy['StudentID'].isin(course_students['Student_ID'])) &
            (~demographics_df_copy['Grad_term'].isna())
            ]

        course_students_graduated = course_students[
            course_students['Student_ID'].isin(students_graduated['StudentID'])
        ]

        course_students_non_graduated = course_students[
            ~course_students['Student_ID'].isin(students_graduated['StudentID'])
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

#def num_math_courses(demographics_df, major_code, years, math_grades_df = None, ftfy = True, grade_options = None):

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
        major_code_student_ids = major_code_students_df['StudentID'].unique()

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
        filtered_demographics_df = demographics_df[(demographics_df['StudentID'].isin(major_code_students_course['Student_ID'].unique())) & (demographics_df['SDSTUDEMOG_TERM'] == demographics_df['SDSTUMAIN_MATRIC_TERM'])]
        filtered_demographics_df = filtered_demographics_df[['StudentID', 'SDSTUMAIN_MATRIC_TERM', 'SDSTUMAIN_MAJOR']]

        filtered_demographics_df['SDSTUMAIN_MATRIC_TERM'] = pd.to_datetime(filtered_demographics_df['SDSTUMAIN_MATRIC_TERM'], format='%Y%m')
        filtered_demographics_df.rename(columns={'SDSTUMAIN_MAJOR': 'Major_at_Matriculation'}, inplace=True)
        current_df = pd.merge(major_code_students_course_earliest, filtered_demographics_df, left_on='Student_ID', right_on='StudentID', how='left')
        current_df['Years Between'] = (current_df['Reg_Term'].dt.year - current_df['SDSTUMAIN_MATRIC_TERM'].dt.year) + current_df['Reg_Term'].dt.month / 12 - current_df['SDSTUMAIN_MATRIC_TERM'].dt.month /12
        current_df.drop('Student_ID', axis=1, inplace=True)

        combined_df = pd.concat([combined_df, current_df], ignore_index=True)

        #drop anomalously duplicated rows
        combined_df.drop_duplicates(subset=['StudentID', 'Reg_Crn', 'Reg_Term', 'Final_GRDE'], keep="first",inplace=True)
    return combined_df


def plot_grades(grades_df, letterGrades = False, title = 'Frequency Diagram of Grades'):
    #if letterGrades:
        # Define the custom bins
        custom_bins = ['A', 'B', 'C', 'D', 'F', 'W']
        # Convert the Final_GRDE_Simplified column to categorical data with custom ordering

        # Drop rows with '#NAME?' values in the Final_GRDE column
        grades_df = grades_df[grades_df['Final_GRDE'] != '#NAME?']

        #simplify letter grades
        grades_df['Final_GRDE_Simplified'] = utilityfunctions.letter_grade_simplify(grades_df['Final_GRDE'])

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


#2023-08-23 student_ids should ber a list of all student ID numbers analyzed for retention
#this can be created via list(df['StudentID'].unique()) for all students, or a list of the students who matriculated
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
    working_df = demographics_df[demographics_df['StudentID'].isin(student_ids)]

    # NOTE (2023-08-14) this analysis excludes those who earn two BS to keep things simple; not sure this is the best approach
    mask = working_df.duplicated(subset=['StudentID', 'SDSTUDEMOG_TERM'], keep=False)  # Create a mask for duplicate rows where a student earns two degrees
    working_df = working_df[~mask]  # Apply the mask to keep only non-duplicate rows; that is, exclude those students who earned two BS
    #print(len(working_df))

    #loop through years and semesters to generate flags
    for academicyear in years:
        semesters = utilityfunctions.create_semesters([academicyear])

        # Filter to semesters associated with argument years
        df_filtered = working_df[working_df['SDSTUDEMOG_TERM'].isin(semesters)]
        #print(len(df_filtered))
        for student in student_ids:
            student_df = df_filtered[df_filtered['StudentID'] == student]

            for semester in semesters:
                semester_df = student_df[student_df['SDSTUDEMOG_TERM'] == semester]

                if semester_df.empty:
                    continue

                #Flag non-graduated students as 0 and graduated students as 1
                #TO DO: Find a way for grad_flag to be set to 1 for the last semester of the degree rather than fixed characteristic
                if (semester_df[((semester_df['StudentID'] == student) & (semester_df['Grad_term']) > 0)].empty):
                    grad_flag = 0
                else:
                    grad_flag = 1

                #indicate if student is still in the indicated major for this semester
                major_retention_flag = int((semester_df['SDSTUMAIN_MAJOR'] == major_code).all())
                major = semester_df['SDSTUMAIN_MAJOR'].item()
                grad_term = semester_df['Grad_term'].item()

                #add the semester and data for current student to the records list
                records.append({
                    'StudentID': student,
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
    major_retention_df= major_retention_df.groupby('StudentID').apply(calculate_running_retention_flag).reset_index(drop=True)

    #for students who changed major, it is helpful to know when they did this to determine where the curriculum structure could be affecting their decisions
    major_changed_df = major_retention_df[major_retention_df['major'] != major_code]  # create dataframe comprised of all students who changed to a different major
    major_changed_df = major_changed_df.reset_index(drop=True)  # reset index to ensure it is contiguous
    major_changed_df = major_changed_df.sort_values(by=['Semester'], ascending=True)
    idx = major_changed_df.groupby('StudentID')['Semester'].idxmin()  # Find index of row with smallest 'Semester' for each 'StudentID'
    major_changed_df = major_changed_df.loc[idx]
    major_changed_df.rename(columns={'Semester': 'major_change_semester'},inplace=True)  # rename the column to avoid confusion
    major_retention_df = pd.merge(major_retention_df, major_changed_df[['StudentID', 'major_change_semester']], on='StudentID', how = 'left', validate = 'many_to_one')

    #Determine how many semesters passed before student changed major
    #Group by 'StudentID' and 'major_change_semester', then apply a lambda function to calculate the count
    semesters_before_major_change_df = (
        major_retention_df.groupby(['StudentID', 'major_change_semester'])
        .apply(lambda x: (x['Semester'] < x['major_change_semester']).sum())
        .reset_index(name='semesters_before_major_change')
    )
    major_retention_df = pd.merge(major_retention_df, semesters_before_major_change_df, on=['StudentID', 'major_change_semester'], how ='left')
    #major_retention_df['total_semesters'] = major_retention_df.groupby('StudentID').size()
    major_retention_df['total_semesters'] = major_retention_df.groupby('StudentID')['StudentID'].transform('size')

    #Create a dataframe reportingt those who graduated that includes the last semester of their BS coursework
    grad_df = major_retention_df[(major_retention_df['grad_flag'] == 1)]  # creates a dataframe comprised of all students who graduated
    grad_df = grad_df.reset_index(drop=True)  # reset the index to ensure it is contiguous
    #grad_df['semesters_till_graduation'] = grad_df.groupby('StudentID').size()
    idx_last_semester = grad_df.groupby('StudentID')['Semester'].idxmax()  # Find the index of the row with the largest 'Semester' for each 'StudentID'

    #idx_first_semester = grad_df.groupby('StudentID')['Semester'].idxmin()
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
        demographics_df['StudentID'].isin(combined_filtered_results['StudentID'].unique())].sort_values(
        by='SDSTUDEMOG_TERM')
    result = sorted_df.drop_duplicates(subset='StudentID', keep='first')

    #create a flag for graduation (1 = graduated, 0 = not graduated)
    result = result.copy() #using .copy() avoids wraning "a value is trying to be set on a copy of a slice from a DataFrame"
    result.loc[:, 'grad_flag'] = result['Grad_term'].notnull().astype(int)

    #select the desired columns from the dataset and derive additional columns
    new_result = result[
        ['StudentID', 'SDSTUDEMOG_SEX', 'SDSTUDEMOG_TERM', 'SDSTUMAIN_MATRIC_TERM', 'Major', 'BirthYear', 'grad_flag']].copy()
    new_result['matriculation_year'] = new_result['SDSTUMAIN_MATRIC_TERM'].apply(lambda x: str(int(x))[:4])
    new_result['age_at_matriculation'] = new_result['matriculation_year'].astype(int) - new_result['BirthYear'].astype(
        int)

    #merge the information
    filtered_testresults = pd.merge(
        left=combined_filtered_results,
        right=new_result[['StudentID', 'age_at_matriculation', 'SDSTUDEMOG_SEX', 'grad_flag', 'Major']],
        on='StudentID', how='left'
    )

    return filtered_testresults
