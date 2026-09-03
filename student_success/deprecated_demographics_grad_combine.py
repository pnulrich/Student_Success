"""
Deprecated module for combining demographics and graduation records.

This script was originally designed to de-identify and collate student data by:
- Scrambling student IDs using a cipher
- Dropping unnecessary columns
- Combining demographics reports with graduation records
- Exporting the result as a CSV for analysis

It uses `tkinter` dialogs to allow manual file selection and pandas for data
manipulation. Compared to equivalent R scripts, this approach was significantly
faster (up to ~100x) for scrambling IDs and merging records.

Functions
---------
- collate_math_grades(course_number_mapping=False) :
    Reads and concatenates multiple CSVs of math course grades, optionally mapping
    course titles to course numbers.
- demographics_grad_combine(cipher=None) :
    Prompts the user to select demographics and graduation CSVs, scrambles student IDs,
    merges the datasets, and exports a combined CSV with a timestamped filename.

Notes
-----
- This module is **deprecated** and retained for archival purposes only.
- Core functionality has been migrated to the refactored `student_success` package.
- Interactive file selection (via `tkinter`) and direct file export make it unsuitable
  for automated pipelines.

See Also
--------
student_success.utils.io_utils : Updated utilities for file handling
student_success.metrics.flagging : Standardized classification scripts
"""


# Python script to de-identify data sets by scrambling ID's and droppping unnceccesary columns. Generates a CSV for analysis.
# Python pandas is much more efficient than R and accomplishes scrambling ID's perhaps 100X faster.
import tkinter.filedialog

import pandas as pd
from datetime import datetime
from tkinter import filedialog as fd
import tkinter as tk
import student_success.deprecated_utilityfunctions as utilityfunctions


#collate rows from CSV files of user-selected math courses and drop unnecessary columns
def collate_math_grades(course_number_mapping = False):
    """
    Reads and combines multiple CSV files containing math grades into a single DataFrame.

    Parameters
    ----------
    course_number_mapping : dict or False, optional
        A dictionary mapping course titles to course numbers. If provided, a new column
        'Course_Number' will be created based on this mapping. (default is False)

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the combined data from all input CSV files.

    """

    # Prompt the user to select CSV files
    root = tk.Tk()
    root.withdraw()
    file_paths = fd.askopenfilenames(filetypes=[('CSV Files', '*.csv')])

    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame()

    # Read and concatenate the CSV files
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Select the desired columns
    selected_columns = ['Reg_Term', 'Course_Dept', 'Instr_Name', 'Reg_Crn', 'Reg_Crse_Title', 'ID', 'Final_GRDE',
                        'StuMajr_Code1']
    combined_df = combined_df[selected_columns]
    combined_df.rename({"ID": "Student_ID"}, axis="columns", inplace=True)

    # Create a new column based on the dictionary mapping 'Reg_Crse_Title' to 'Course_Number'
    if course_number_mapping:
        combined_df['Course_Number'] = combined_df['Reg_Crse_Title'].map(course_number_mapping)
        print(combined_df['Course_Number'])

    return combined_df


#Joins demographics reports with graduation records in a single dataframe
def demographics_grad_combine(cipher = None):
    """
    Combines demographics reports with graduation records into a single DataFrame.

    Parameters
    ----------
    cipher : str or None, optional
        A cipher value used to obscure student IDs. (default is None)

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing combined demographics and graduation data.

    Notes
    -----
    - The function prompts the user to select CSV files for demographics and graduation records.
    - Demographics and graduation data are merged based on student ID.
    - Duplicate rows with the same term and student ID are eliminated.
    - The output DataFrame is saved as a CSV file in a user-defined folder with a filename
      suffix in YYYYMMDD format.

    """

    if (cipher == None):
        print("You must provide a cipher value to use this function in order to obscure student IDs.")
        return

    demographics_data_filename = fd.askopenfilename(title = 'CV Enrollment Academic Program 1 and 2 DB S440270') # show an "Open" dialog box and return the path to the selected file
    print(demographics_data_filename)
    demographics_data = pd.read_csv(demographics_data_filename)
    demographics_data.rename({"PantherID": "Student_ID"}, axis="columns", inplace=True) #using Student_ID as standard

    print(list(demographics_data))

    demographics_data = demographics_data[
        [
            "SDSTUDEMOG_TERM",
            "Student_ID",
            "SDSTUDEMOG_BIRTHDATE",
            "SDSTUDEMOG_ETHNICITY_CODE",
            "SDSTUDEMOG_RACE",
            "SDSTUDEMOG_SEX",
            "SDSTUDEMOG_COUNTY_ORIGIN_MATIC",
            "SDSTUDEMOG_STATE_ORIGIN_MATRIC",
            "SDSTUDEMOG_ADDRESS_LINE_1",
            "SDSTUDEMOG_ADDRESS_LINE_2",
            "SDSTUDEMOG_CITY",
            "SDSTUDEMOG_STATE",
            "SDSTUDEMOG_ZIPCODE",
            "SDSTUDEMOG_FINANCIAL_AID_IND",
            "SDSTUMAIN_MATRIC_TERM",
            "SDSTUMAIN_TERM",
            "SDSTUMAIN_MAJOR",
            "SDSTUMAIN_MAJOR2",
            "SDSTUMAIN_HOURS_ENROLLED",
            "SDSTUMAIN_HOURS_EARNED",
            "SDSTUMAIN_HOURS_ATTEMPTED",
            "SDSTUMAIN_HOURS_TOTAL",
            "SDSTUMAIN_TRANSFER_HOURS",
            "SDSTUMAIN_TRANSFER_GPA",
            "SDSTUGPA_HOURS_ATTPT_INST",
            "SDSTUGPA_HOURS_EARNED_INST",
            "SDSTUGPA_GPA_INST",
        ]
    ]

    #demographics_data['SDSTUMAIN_MATRIC_TERM'] = demographics_data['SDSTUMAIN_MATRIC_TERM'].astype('int64')

    #use secret cipher to obscure identifer
    demographics_data = utilityfunctions.scramble_ID(demographics_data, cipher)

    # Keep only year of birth
    demographics_data.rename(
        {"SDSTUDEMOG_BIRTHDATE": "BirthYear"}, axis="columns", inplace=True
    )
    demographics_data["BirthYear"] = demographics_data["BirthYear"].str[-4:]

    # Eliminate any rows where Term and Student_ID are both duplicated
    len(demographics_data)
    demographics_data = demographics_data[
        ~demographics_data.duplicated(subset=["SDSTUDEMOG_TERM", "Student_ID"], keep="first")
    ]
    len(demographics_data)
    # print(demographics_data.head())

    # Load graduates data file
    graduates_data_filename = fd.askopenfilename(title = 'Graduation Purge Report S761102')
    graduates_data = pd.read_csv(graduates_data_filename)
    graduates_data.rename({"Csv_id": "Student_ID"}, axis="columns", inplace=True)

    # use secret cipher to obscure identifer
    graduates_data = utilityfunctions.scramble_ID(graduates_data, cipher)
    graduates_data = graduates_data[
        graduates_data.columns[~graduates_data.columns.isin(["Student_name", "Pidm"])]
    ]
    len(graduates_data)
    graduates_data = graduates_data[
        ~graduates_data.duplicated(subset=["Student_ID", "Grad_term"], keep="first")
    ]
    len(graduates_data)


    # Join datasets based on student ID number
    # yields 1060505 rows x 38 columns; this differs from R process in utilityFunctions.r. My R function yields 1089475 rows.
    demographics_data_combined = demographics_data.merge(
        graduates_data, on="Student_ID", how="left"
    )

    demographics_data_combined['Grad_year'] = demographics_data_combined['Grad_year'].fillna(-1)
    demographics_data_combined['Grad_year'] = demographics_data_combined['Grad_year'].astype('int64')
    demographics_data_combined['Grad_term'] = demographics_data_combined['Grad_term'].fillna(-1)
    demographics_data_combined['Grad_term'] = demographics_data_combined['Grad_term'].astype('int64')
    demographics_data_combined['SDSTUMAIN_MATRIC_TERM'] = demographics_data_combined['SDSTUMAIN_MATRIC_TERM'].fillna(-1)
    demographics_data_combined['SDSTUMAIN_MATRIC_TERM'] = demographics_data_combined['SDSTUMAIN_MATRIC_TERM'].astype('int64')

    # save combined data set into user defined folder with filename suffix as YYYYMMDD format
    new_csv_path = fd.askdirectory(title = "Select folder to save CSV") + "/S440270_GraduationPurge_Combined_" + datetime.today().strftime('%Y%m%d') + ".csv"
    demographics_data_combined.to_csv(new_csv_path, encoding="utf-8", index=False)
    #demographics_data_combined["BirthYear"] = demographics_data_combined["BirthYear"].astype('int64')
    print("Data exported to " + new_csv_path)
