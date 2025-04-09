import numpy as np
import pandas as pd
from institutionaldata.utils.constants import PEER_ABBREVIATION_DICT, PEER_DESCRIPTION_DICT, SEX_DICT
from institutionaldata.utils.validation import validate_columns


def set_up_demographic_flags(df, peer=True, hispanic=True, pell=True, first_generation=True, sex=True):
    """
    Adds binary demographic flags to a student-level DataFrame.

    This function creates new columns that represent:
    - PEER status (based on race and optionally ethnicity)
    - Hispanic ethnicity
    - PELL grant eligibility
    - First-generation status
    - Sex (binary flag)

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing demographic data for students.
    peer : bool, default=True
        If True, adds a 'flag_PEER' column based on race (and optionally Hispanic status).
    hispanic : bool, default=True
        If True, adds a 'flag_hispanic' column for Hispanic ethnicity (using either
        'demographics_hispanic' or 'demographics_ethnicity').
    pell : bool, default=True
        If True, adds a 'flag_PELL' column based on PELL grant eligibility.
    first_generation : bool, default=True
        If True, adds a 'flag_first_generation' column based on first-gen college status.
    sex : bool, default=True
        If True, adds a 'flag_sex' column based on sex (1 = Female, 0 = Male).

    Returns
    -------
    pandas.DataFrame
        A copy of the original DataFrame with added flag columns, depending on options selected.

    Notes
    -----
    - PEER definitions:
        * Race values of 'Black or African American', 'American Indian or Alaska Native',
          'Pacific Islander', and multiracial may contribute to PEER status.
        * If `hispanic=True`, students marked as Hispanic override PEER status if their race
          would otherwise result in exclusion.
    - Sex flag uses values from `SEX_DICT`, which maps both 'F'/'M' and 'Female'/'Male'.
    - Sex and race taxonomy can be updated in institutionaldata.utils.constants.py as needed
    - Missing or unrecognized values default to 0 or -1 where appropriate.
    """

    df = df.copy()

    required_columns = []
    if hispanic:
        required_columns.append('demographics_hispanic')
        # fallback logic allows either column, so don’t validate both
        if 'demographics_hispanic' not in df.columns and 'demographics_ethnicity' not in df.columns:
            raise ValueError(
                "Missing both 'demographics_hispanic' and 'demographics_ethnicity' columns required for Hispanic flag.")
    if peer:
        required_columns.append('demographics_race')
    if sex:
        required_columns.append('demographics_sex')
    if first_generation:
        required_columns.append('flag_first_generation')
    if pell:
        required_columns.append('flag_PELL')
    # Validate required columns
    validate_columns(df.columns, required_columns)

    if hispanic:
        if 'demographics_hispanic' in df.columns:
            df['flag_hispanic'] = 0
            hispanic_dict = {'Non-Hispanic': 0, 'Hispanic': 1}
            df['flag_hispanic'] = df['demographics_hispanic'].map(hispanic_dict).fillna(0).astype("int8")

        elif 'demographics_ethnicity' in df.columns:
            df['flag_hispanic'] = 0
            df['flag_hispanic'] = df['demographics_ethnicity'].map({1:0, 2:1}).fillna(0).astype("int8")

    # Convert abbreviations to full text using mapping
    if peer:
        # Initialize flag with default value for non-matches
        df['flag_PEER'] = 0

        # Function to determine PEER status
        def determine_peer(race_str):
            # Check for direct matches in full descriptions
            if race_str in PEER_DESCRIPTION_DICT:
                return PEER_DESCRIPTION_DICT[race_str]

            # Handle abbreviations
            if isinstance(race_str, str):
                # Split multi-letter abbreviations and map each to the full description
                matches = [PEER_DESCRIPTION_DICT[PEER_ABBREVIATION_DICT[letter]] for letter in race_str if
                           letter in PEER_ABBREVIATION_DICT]
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
            mask = (df['flag_hispanic'] == 1) & (df['flag_PEER'].isin([0, -1, 2]))
            df.loc[mask, 'flag_PEER'] = 1

    if sex:
        df['flag_sex'] = df['demographics_sex'].map(SEX_DICT).fillna(-1).astype(int)

    if first_generation:
        df['flag_first_generation'] = df['flag_first_generation'].replace({'Y': 1, 'N': 0, np.nan: 0}).astype(int)

    if pell:
        df['flag_PELL'] = df['flag_PELL'].replace({'Y': 1, 'N': 0, np.nan: 0}).astype(int)

    return df


def demographics_first_semester(df, transfer_status="any", return_dataframe = 1):
    """
    Returns the first-term demographics record for each student, optionally filtered by transfer status.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing student demographic records across multiple terms.
    transfer_status : {'any', 'with', 'without'}, default='any'
        Specifies which students to include based on transfer credit status:
        - 'any': include all students
        - 'with': include only students with transfer credit in their first term
        - 'without': include only students with no transfer credit in their first term
    return_dataframe : int, default=1
        - 1: returns a DataFrame of the first-term records
        - 0: returns a list of student_ID values

    Returns
    -------
    pandas.DataFrame or list
        Either a DataFrame of first-term demographic records or a list of student_IDs,
        depending on the value of `return_dataframe`.

    Raises
    ------
    ValueError
        If `transfer_status` is not one of {'any', 'with', 'without'}.

    Notes
    -----
    - First-term status is determined using the earliest `demographics_term` for each student.
    - The column 'transfer_hours_term' is used to determine transfer credit status.
    """

    df = df.copy()

    if transfer_status not in {'any', 'with', 'without'} :
        raise ValueError("transfer_status must be one of the following: 'any', 'with', or 'without")

    required_columns = ['student_ID', 'demographics_term', 'transfer_hours_term']
    validate_columns(df.columns, required_columns)

    # Get the earliest term for each student
    mask = df.groupby('student_ID')['demographics_term'].idxmin()
    earliest_df = df.loc[mask]

    # return dataframe containing first semester demographics for ALL students
    if (transfer_status == 'any'):
        if return_dataframe == 1:
            return earliest_df
        elif return_dataframe == 0:
            return list(earliest_df['student_ID'])

    # return dataframe containing first semester demographics for students who WITH transfer credit
    elif (transfer_status == 'with'):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['transfer_hours_term'] > 0) & (~earliest_df['transfer_hours_term'].isna())]
        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['student_ID'])

    # return dataframe containing first semester demographics for students WITHOUT transfer credit
    elif (transfer_status == 'without'):
        initial_demographics_transfer_df = earliest_df[
            (earliest_df['transfer_hours_term'].isna()) | (earliest_df['transfer_hours_term'] == 0)]

        if return_dataframe == 1:
            return initial_demographics_transfer_df
        elif return_dataframe == 0:
            return list(initial_demographics_transfer_df['student_ID'])
