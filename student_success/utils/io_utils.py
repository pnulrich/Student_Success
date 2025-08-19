"""
io_utils.py

Utilities for loading, concatenating, and renaming data files in the
student_success package.

This module provides functions that:
- Concatenate multiple CSVs into one DataFrame.
- Prompt users interactively to load a CSV of grades.
- Rename DataFrame columns in bulk based on an external Excel mapping file.
- Extract and flatten column mapping dictionaries from Excel codebooks.

Institutional Customization
---------------------------
Each institution has unique data exports and column naming conventions.
These utilities let you standardize your raw data to match the expected
column names used across the package.

- Column mapping:
  The Excel codebook (default sheet name: "codebook") must contain at least
  `variable_name_project` (standardized name) and `variable_name_institution`
  (your institution’s export names).
  Update or expand this file to align with your SIS exports.
- File handling:
  Paths to CSV and Excel files must be accessible from your environment.
  If using interactive `load_grades()`, ensure Tkinter is available.

Pitfalls
--------
- `load_grades()` uses a Tkinter dialog; this may not work in headless
  environments (e.g., servers, notebooks without GUI). In those cases,
  load CSVs directly with `pandas.read_csv()`.
- Duplicates in the Excel column mapping can create ambiguous renaming.
  Check the flattened dictionary output carefully.
- If the Excel codebook format changes (sheet name, column names),
  `extract_column_mapping()` will need updates.

Contents
--------
- concatenate_csv_files(filenames, low_memory=False) :
  Read and combine multiple CSV files into a single DataFrame.
- load_grades() :
  Open a file dialog to select and load a grades CSV; returns DataFrame.
- rename_columns_in_bulk(df, column_mapping_filepath) :
  Rename DataFrame columns using a flattened mapping from an Excel file.
- extract_column_mapping(file_path) :
  Read an Excel sheet and return nested dictionary mapping
  project → [institution names].
- flatten_column_mapping(column_mapping) :
  Convert a nested column mapping into a flat dictionary for renaming
  (institution name → project name).

Notes
-----
- These utilities are designed to be run early in preprocessing so that
  column names match expected inputs for hazard, Sankey, or Markov analyses.
- Requires `openpyxl` for Excel parsing.
"""

import pandas as pd
from tkinter import filedialog as fd
import openpyxl  # necessary for importing the Excel column naming file; placing here so it isn't missed in requirements_essential.txt


def concatenate_csv_files(filenames, low_memory=False):
    # Create an empty list to hold each dataframe
    dataframes = []

    # Loop through the list of filenames
    for file in filenames:
        # Read each CSV file and append the dataframe to the list
        df = pd.read_csv(file, low_memory=low_memory)
        dataframes.append(df)

    # Concatenate all dataframes into one
    concatenated_df = pd.concat(dataframes, ignore_index=True)

    return concatenated_df


# Utility function: gets user input on which CSV grades reports files to load and returns as a pandas dataframe
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

    csv_filename = fd.askopenfilename(title='Please select the grades file')  # show an "Open" dialog box and return the path to the selected file
    if not csv_filename:
        print("No file selected.")
        return pd.DataFrame()  # or raise an Exception or return None

    print(csv_filename)
    grades_df = pd.read_csv(csv_filename)
    return grades_df


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
    df = pd.read_excel(file_path, sheet_name='codebook', engine='openpyxl')
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
