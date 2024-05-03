#@profile
def my_func():
    import os
    from dotenv import load_dotenv
    import pandas as pd
    import numpy as np
    import sys
    sys.path.append('../../')
    import institutionaldata.successmetrics
    import institutionaldata.utilityfunctions
    import importlib
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.formula.api import ols
    import scipy.stats as stats
    import matplotlib.pyplot as plt
    import seaborn as sns

    load_dotenv()
    import importlib
    #Rename columns to standardized names
    column_mapping_file_path = r'C:\Research\Research Projects\GSU\HHMI_IE3\Analyses\HHMI_Student_Success\institutionaldata\column_mapping.tsv'
    courses_df = pd.read_csv(r'C:\Research\Research Projects\GSU\HHMI_IE3\Analyses\Datasets\Bio_Major_Courses (Elaine, 2024-04-22)\HHMI 4.22.csv')
    courses_df = institutionaldata.utilityfunctions.rename_columns_in_bulk(courses_df, column_mapping_filepath = column_mapping_file_path)

    #Deidentify student IDs and create demographic flags
    courses_df = institutionaldata.utilityfunctions.scramble_ID(courses_df, cipher=os.environ['STUDENT_SUCCESS_CIPHER'])
    courses_df = institutionaldata.utilityfunctions.set_up_demographic_flags(df = courses_df)

    # Remove leading and trailing spaces from values in the 'course_title' column
    courses_df.loc[:,'course_title'] = courses_df['course_title'].str.strip()

    # Data Preparation
    courses_df.loc[:, 'course_term'] = pd.to_datetime(courses_df['course_term'], format='%Y%m')
    courses_df.loc[:, 'year'] = courses_df['course_term'].dt.year
    courses_df.loc[:, 'semester'] = courses_df['course_term'].dt.month.apply(lambda x: 'Spring' if x == 1 else ('Summer' if x == 5 else 'Fall'))

    # Calculate numerical grade from letter grade
    courses_df.loc[:,'course_grade_letter'] = courses_df['course_grade_letter'].astype(str)
    courses_df.loc[:,'course_grade_numeric'] = courses_df['course_grade_letter'].apply(institutionaldata.utilityfunctions.num_grade_institutional)

    # Simplify letter grades for ease of filtering to get DFW
    courses_df = institutionaldata.utilityfunctions.letter_grade_simplify(dataframe = courses_df, c_minus_flag= False)

    # Create  flag for a given course being taken at PC (associates level)
    courses_df.loc[:, 'flag_course_PC'] = (courses_df['course_college'] == 'PC').astype(int)


    # Courses: BIOL 2107K, BIOL 2108K, CHEM 1211K, CHEM 1212K
    # Time Range: 201201-201808
    # Major at Matriculation: BIO
    # Include withdrawals: No
    # Include summer term: No
    end_date = pd.to_datetime('201808', format='%Y%m')
    start_date = pd.to_datetime('201201', format='%Y%m')
    grades_df = courses_df[(courses_df['major_matriculation'] == 'BIO') & (courses_df['course_prefix'].isin(['BIOL', 'CHEM'])) & (courses_df['course_number'].isin([1211, 1212, 2107,2108])) & (courses_df['course_term']<=end_date) & (courses_df['course_term']>= start_date) & (courses_df['course_suffix'] == 'K')]  # takes only those rows for BIOL 2107 and 2108
    grades_df = grades_df.copy()
    grades_df = grades_df[grades_df['course_grade_numeric'] >= 0] # do not include withdrawals in dataset
    grades_df = grades_df[(grades_df['semester'] != 'Summer')]

    # Creating a flag for retake amd keep only the first instance
    grades_df.sort_values(by=['student_ID', 'course_number', 'course_term'], inplace=True)
    grades_df.loc[:, 'is_retake'] = grades_df.duplicated(subset=['student_ID', 'course_number'], keep='first').astype(int)

    # Calculate proportion of minority students in each class. 'COURSE_XLIST' identifier used for grouping to ensure that lecture classmates used for measure of cohort characteristics
    grades_df.loc[:, 'minority_proportion'] = grades_df.groupby(['course_number', 'course_suffix', 'course_term', 'year', 'COURSE_XLIST'])['flag_PEER'].transform('mean')

    # Calculate standardized grades utilizing Sovero et al. method
    grades_df.loc[:, 'course_mean'] = grades_df.groupby(['course_number', 'course_suffix', 'year'])['course_grade_numeric'].transform('mean')
    grades_df.loc[:, 'course_std'] = grades_df.groupby(['course_number', 'course_suffix', 'year'])['course_grade_numeric'].transform('std')
    grades_df.loc[:, 'standardized_grade'] = (grades_df['course_grade_numeric'] - grades_df['course_mean']) / grades_df['course_std']
    grades_df.loc[:, 'standardized_grade'] = grades_df['standardized_grade'].fillna(0) # Handle cases with only one student in a course-term

    # Calculate adjusted minority_proportion
    grades_df.loc[:, 'adjusted_minority_proportion'] = grades_df['minority_proportion'] * grades_df['course_std']

    # Convert select variables to lower memory types
    #grades_df['course_number'] = grades_df['course_number'].astype('category') #categories may be more memory efficient
    grades_df['flag_PEER'] = grades_df['flag_PEER'].astype('int8')
    grades_df['flag_sex'] = grades_df['flag_sex'].astype('int8')
    grades_df.loc[:, 'demographics_high_school_GPA'] = grades_df['demographics_high_school_GPA'].astype(float)

    # calculating adjusted high school GPA term
    grades_df.loc[:, 'course_high_school_GPA'] = grades_df.groupby(['course_number', 'course_term', 'course_suffix', 'year', 'COURSE_XLIST'])['demographics_high_school_GPA'].transform('mean')
    grades_df['course_high_school_GPA'] = grades_df['course_high_school_GPA'].astype(float) # convert to float
    grades_df.loc[:, 'adjusted_course_high_school_GPA'] = grades_df['course_high_school_GPA'] * grades_df['course_std']
    grades_df['adjusted_course_high_school_GPA'] = grades_df['adjusted_course_high_school_GPA'].astype(float) # convert to float

    # calculating adjusted sex proportion term
    grades_df.loc[:, 'sex_proportion'] = grades_df.groupby(['course_number', 'course_term', 'course_suffix', 'year', 'COURSE_XLIST'])['flag_sex'].transform('mean')
    grades_df.loc[:, 'adjusted_sex_proportion'] = grades_df['sex_proportion'] * grades_df['course_std']
    grades_df.loc[:, 'sex_proportion'] = grades_df.groupby(['course_number', 'course_term', 'course_suffix', 'year', 'COURSE_XLIST'])['flag_sex'].transform('mean')
    grades_df.loc[:, 'adjusted_sex_proportion'] = grades_df['sex_proportion'] * grades_df['course_std']

    # drop rows for students who have no HS GPA (see TODO above for comment)
    print('Number of rows before dropping the ones with no HS GPA: ', len(grades_df))
    grades_df = grades_df.dropna(subset=['demographics_high_school_GPA'])
    print('Number of rows AFTER dropping those with no HS GPA: ', len(grades_df))

    # clean up unused variables to save memory
    del(courses_df)

    # drop unnecessary variables to save memory
    columns_to_keep = ['course_term', 'student_ID', 'course_prefix', 'course_number', 'course_suffix', 'COURSE_XLIST', 'demographics_high_school_GPA', 'flag_first_generation', 'flag_PELL', 'demographics_sex', 'transfer_hours_matriculation', 'demographics_age', 'flag_PEER', 'flag_sex', 'course_grade_numeric', 'is_retake',
                      'minority_proportion', 'course_mean', 'course_std', 'standardized_grade', 'adjusted_minority_proportion', 'course_high_school_GPA', 'adjusted_course_high_school_GPA', 'sex_proportion', 'adjusted_sex_proportion', 'WHKEY_INSTRUCTOR', 'semester', 'year']
    grades_df.loc[:, columns_to_keep]

    print(grades_df.dtypes)

    # List of columns to convert to float16
    columns_to_convert = ['minority_proportion', 'course_mean', 'course_std',
                          'standardized_grade', 'adjusted_minority_proportion',
                          'course_high_school_GPA', 'adjusted_course_high_school_GPA',
                          'sex_proportion', 'adjusted_sex_proportion']

    # Convert specified columns to float16
    grades_df[columns_to_convert] = grades_df[columns_to_convert].astype('float16')
    print(grades_df.dtypes)


    # Report memory use
    memory_usage = grades_df.memory_usage(deep=True).sum() / (1024 ** 2)  # Convert bytes to megabytes
    print("Memory Usage:", memory_usage, "MB")

    model_formula = 'standardized_grade ~ 1 + C(student_ID) + C(course_number)'
    mixedlm_model = smf.mixedlm(model_formula, grades_df, groups=grades_df['student_ID'], use_sparse=True)
    mixedlm_result = mixedlm_model.fit()

    # Diagnostics: Plotting residuals for normality check and homoscedasticity
    residuals = mixedlm_result.resid
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title('Q-Q plot of residuals')
    plt.show()

    plt.scatter(mixedlm_result.fittedvalues, residuals)
    plt.title('Residuals vs Fitted Values')
    plt.xlabel('Fitted values')
    plt.ylabel('Residuals')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.show()

    print(mixedlm_result.summary())

if __name__ == '__main__':
    my_func()