import pandas as pd
import numpy as np
from datetime import datetime
import math

def adjust_grad_term(date):
    """
    Adjust graduation term based on the given month.

    Parameters
    ----------
    date : pandas.Timestamp or datetime.datetime
        A datetime object representing the original graduation date.

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
    >>> adjust_grad_term(pd.Timestamp('2022-01-15'))
    Timestamp('2022-05-15 00:00:00')

    >>> adjust_grad_term(pd.Timestamp('2022-05-01'))
    Timestamp('2022-08-01 00:00:00')

    >>> adjust_grad_term(pd.Timestamp('2022-08-30'))
    Timestamp('2022-12-30 00:00:00')

    >>> adjust_grad_term(pd.NaT)
    NaT
    """

    if pd.isna(date):  # This checks for NaN values
        return pd.NaT
    if date.month == 1:
        return date.replace(month=5)
    elif date.month == 5:
        return date.replace(month=8)
    elif date.month == 8:
        return date.replace(month=12)
    else:
        return date

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
            semesters.extend(semesterList)
            semesters.sort()
        return sorted(semesters)

    else:
        for year in years:
            spring = year * 100 + 1
            summer = year * 100 + 5
            fall = (year-1) * 100 + 8
            semesterList = list([spring,summer, fall])
            semesters.extend(semesterList)
        return sorted(semesters)


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



def get_nth_year_fall_term(term_series, year=3, return_as_datetime=True):
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
    >>> get_nth_year_fall_term(sample_series_yyyymm, year=3)
    0   2012-08-01
    1   2012-08-01
    2   2012-08-01
    dtype: datetime64[ns]

    >>> get_nth_year_fall_term(sample_series_yyyymm, year=3, return_as_datetime=False)
    0    201208
    1    201208
    2    201208
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
    nth_year_fall_year = start_year + year - 1 # 1 is subtracted because start year is year #1

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
    return int(year_code + semester_code)

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

def calculate_semester_interval(semester_A, semester_B):
    """
    Calculate the number of academic semesters between semester_A and semester_B.

    This function assumes a forward academic sequence: Spring (01), Summer (05), Fall (08).
    It raises an error if semester_A is after semester_B.

    Parameters
    ----------
    semester_A : int
        The starting term code in format YYYYMM.
    semester_B : int
        The ending term code in format YYYYMM.

    Returns
    -------
    int
        The number of semesters between semester_A and semester_B.

    Raises
    ------
    ValueError
        If semester_A is later than semester_B.

    Examples
    --------
    >>> calculate_semester_interval(202308, 202401)
    1
    >>> calculate_semester_interval(202308, 202405)
    2
    >>> calculate_semester_interval(202308, 202305)
    ValueError: semester_A (202308) must not be after semester_B (202305)
    """

    if semester_A > semester_B:
        raise ValueError(f"Semester A ({semester_A}) must not be after Semester B ({semester_B})")


    # Semester sequence within academic year: Fall (08), Spring (01), Summer (05)
    semester_sequence = ['08', '01', '05']

    current_year = int(str(semester_A)[:4])
    current_semester = str(semester_A)[4:]
    max_year = int(str(semester_B)[:4])
    max_semester = str(semester_B)[4:]

    # Adjust year for Fall semester
    if current_semester == '08':
        current_year += 1
    if max_semester == '08':
        max_year += 1

    # Calculate total semesters missed
    semesters_between = 0

    # Start from the current semester's position
    next_semester_index = semester_sequence.index(current_semester)
    checking_year = current_year

    while True:
        # Move to next semester in sequence
        next_semester_index = (next_semester_index + 1) % 3

        # If we've completed the sequence and are starting a new year
        if next_semester_index == 0:
            checking_year += 1

        # Adjust year back if we're constructing a Fall term
        if semester_sequence[next_semester_index] == '08':
            term_year = checking_year - 1

        else:
            term_year = checking_year

        # Construct the next term to check
        next_term = int(f"{term_year}{semester_sequence[next_semester_index]}")

        # Stop if we've reached or exceeded the max term
        if next_term > semester_B:
            break

        # Increment missed semesters
        semesters_between += 1

    return semesters_between


# Define function to combine spring/summer based on presence of both terms
def combine_spring_summer_terms(df, remove_original = False):
    """
    Combines spring (YYYY01) and summer (YYYY05) terms into a single term per year for each student,
    while retaining all original columns in the dataframe. New combined rows are created with
    `demographics_term` set to a unique code (`YYYY04.xx`) and appended to the dataframe unless
    `remove_original=True`.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe containing at least the following columns:
        - 'student_ID' : Identifier for each student.
        - 'demographics_term' : Term codes in YYYYMM integer format (e.g., 202301 for Spring 2023).
        - Additional demographic columns to retain in the combined rows.

    remove_original : bool, optional (default=False)
        If True, removes the original spring (YYYY01) and summer (YYYY05) term rows after creating the combined rows.

    Returns
    -------
    pandas.DataFrame
        The original dataframe with additional rows for each combined spring-summer term.
        Each new combined row contains:
        - 'student_ID' : Same as in the original rows.
        - 'demographics_term' : One of the following combined codes:
            - YYYY04.11 → if both spring and summer terms are present
            - YYYY04.10 → if only the spring term is present
            - YYYY04.01 → if only the summer term is present
          The decimal portion encodes term presence (1 = present, 0 = absent): `.10` = spring only, `.01` = summer only, `.11` = both.
        - 'term_type' : A human-readable indicator of the term type:
            - 'spring+summer', 'spring', or 'summer'
        - All other columns are copied from the appropriate term row, with summer taking precedence when both are present.

    Notes
    -----
    - This function assumes that `demographics_term` is stored as an integer.
    - A temporary column 'year' is added to support grouping and removed before returning the result.
    - Original spring and summer rows are retained by default to allow flexible filtering; set `remove_original=True` to exclude them.

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

    # Extract year and create term masks
    df['year'] = df['demographics_term'] // 100
    df['term_code'] = df['demographics_term'] % 100

    # Set 'fall' term_type directly for original fall rows
    df.loc[df['term_code'] == 8, 'term_type'] = 'fall'

    spring_mask = df['term_code'] == 1
    summer_mask = df['term_code'] == 5

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
            combined_row['term_type'] = 'spring+summer'  # for .11
            combined_rows.append(combined_row)
        elif has_spring:
            # Only spring term exists
            combined_code = year * 100 + 4.10
            combined_row = group[spring_mask[group.index]].iloc[0].copy()
            combined_row['demographics_term'] = combined_code
            combined_row['term_type'] = 'spring'  # for .10
            combined_rows.append(combined_row)
        elif has_summer:
            # Only summer term exists
            combined_code = year * 100 + 4.01
            combined_row = group[summer_mask[group.index]].iloc[0].copy()
            combined_row['demographics_term'] = combined_code
            combined_row['term_type'] = 'summer'  # for .01
            combined_rows.append(combined_row)


    # Concatenate the combined rows as a new DataFrame and append in bulk
    combined_df = pd.DataFrame(combined_rows)
    result_df = pd.concat([df, combined_df], ignore_index=True)


    # Optional removal of original spring/summer terms
    if remove_original:
        result_df = result_df[~(result_df['term_code'].isin([1, 5]))]
    result_df = result_df.sort_values(by=['student_ID', 'demographics_term']).reset_index(drop=True)
    result_df.drop(columns=['year', 'term_code'], inplace=True)

    return result_df

def standardize_to_term_code(term):
    """
    Converts float-coded terms (e.g., 202004.11) and standard integers (e.g., 202008)
    into valid YYYYMM format for interval calculations.

    Mapping:
    - .10 → Spring → YYYY01
    - .01 → Summer → YYYY05
    - .11 → Combined → YYYY05
    - .00 or valid int → Passed through

    Notes
    -----
    This function ensures compatibility with calculate_semester_interval()
    by mapping custom-encoded floats into valid 6-digit term codes.
    """

    import pandas as pd
    import math

    if pd.isna(term) or (isinstance(term, float) and math.isnan(term)):
        raise ValueError("Encountered NaN or missing term code.")

    if isinstance(term, float):
        term_str = f"{term:.2f}"
        year_part, suffix = term_str.split(".")
        if len(year_part) == 6:
            year_str = year_part[:4]
        elif len(year_part) == 8:
            # Already improperly formed, use first 4 digits
            year_str = year_part[:4]
        else:
            year_str = year_part

        if suffix == "10":
            return int(f"{year_str}01")
        elif suffix == "01":
            return int(f"{year_str}05")
        elif suffix == "11":
            return int(f"{year_str}05")
        elif suffix == "00":
            return int(f"{year_str}08")
        else:
            raise ValueError(f"Unrecognized suffix '{suffix}' in term '{term}'")

    elif isinstance(term, int):
        if str(term).endswith(("01", "05", "08")):
            return term
        else:
            raise ValueError(f"Invalid MM in standard term code: {term}")

    else:
        raise ValueError(f"Unsupported term code type: {term} ({type(term)})")


