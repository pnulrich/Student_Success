"""

Utility functions for scrambling and unscrambling student IDs using a
digit-to-character cipher.

This module provides functions to anonymize student identifiers for
research and reporting by replacing numeric digits (0–9) with characters
from a user-defined cipher. IDs can be scrambled or unscrambled either
individually (as strings) or in bulk (for pandas DataFrames with a
`student_ID` column).

Functions
---------
- scramble_ID : Scramble student IDs using a 10-character cipher.
- unscramble_ID : Unscramble student IDs back to their original digits
  using the same cipher.

Notes
-----
- The cipher must be a string of exactly 10 characters, mapping each digit
  (0–9) to a substitute character.
- Scrambling removes leading zeros from IDs before applying the cipher.
- Never share or publish your cipher string; treat it as confidential data.
- The scrambled IDs are deterministic: the same input and cipher will always
  produce the same output.
- If `input_data` is a DataFrame, the column `student_ID` must be present.

Examples
--------
Scramble a single ID:
>>> scramble_ID("012345", "abcdefghij")
'abcdefgh'

Scramble a DataFrame:
>>> scramble_ID(df, "abcdefghij")
DataFrame with scrambled student_ID column

Unscramble back:
>>> unscramble_ID("abcdefgh", "abcdefghij")
'012345'
"""


import pandas as pd


def scramble_ID(input_data, cipher):
    """
    Scramble student IDs based on a digit-character cipher.

    Parameters
    ----------
    input_data : pandas.DataFrame or str
        The input to scramble. If a DataFrame, it must contain a column named 'student_ID'.
        If a string, it should be a single student ID to scramble.

    cipher : str
        A string of exactly 10 characters representing a mapping of digits 0–9 to new characters.
        For example, cipher[0] replaces '0', cipher[1] replaces '1', and so on.
        DO NOT POST YOUR CIPHER PUBLICLY.

    Returns
    -------
    pandas.DataFrame or str or None
        - If input_data is a DataFrame, returns a copy with the 'student_ID' column scrambled.
        - If input_data is a string, returns the scrambled student ID.
        - If input_data is neither, returns None.

    Notes
    -----
    - The cipher must contain exactly 10 characters, mapping the digits 0–9.
    - For DataFrames, the 'student_ID' column must be present.
    - Leading zeros in student IDs are stripped before scrambling.
    - Do not post or share your cipher publicly.

    Examples
    --------
    >>> scramble_ID("012345", "abcdefghij")
    'abcdefgh'

    >>> scramble_ID(df, "abcdefghij")
    DataFrame with scrambled student_ID column
    """

    if len(cipher) != 10:  # if student IDs at your institution have different # of unique characters, then adjust accordingly
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

def unscramble_ID(input_data, cipher):
    """
    Unscramble student IDs that were scrambled using a digit-character cipher.

    Parameters
    ----------
    input_data : pandas.DataFrame or str
        The input to unscramble. If a DataFrame, it must contain a 'student_ID' column.
        If a string, it should be a single scrambled student ID.

    cipher : str
        A string of exactly 10 characters representing the cipher used to scramble digits 0–9.
        The position of each character maps back to its original digit (i.e., cipher[0] = char that replaced '0').
        DO NOT POST YOUR CIPHER PUBLICLY.

    Returns
    -------
    pandas.DataFrame or str or None
        - If input_data is a DataFrame, returns a copy with the 'student_ID' column unscrambled.
        - If input_data is a string, returns the unscrambled student ID.
        - If input_data is neither, returns None.

    Notes
    -----
    - The cipher must contain exactly 10 characters, mapping the digits 0–9.
    - This function assumes the scrambling was done using `scramble_ID()` with the same cipher.
    - Do not post or share your cipher publicly.

    Examples
    --------
    >>> unscramble_ID("abcdefghij", "abcdefghij")
    '0123456789'

    >>> unscramble_ID(df, "abcdefghij")
    DataFrame with unscrambled student_ID column
    """

    if len(cipher) != 10:
        print("The cipher must have 10 characters!")
        return None

    unscramble_dict = {char: str(i) for i, char in enumerate(cipher)}

    if isinstance(input_data, pd.DataFrame):
        results_df = input_data.copy()

        if 'student_ID' not in results_df.columns:
            print("The dataframe does not have a 'student_ID' column.")
            return None

        results_df["student_ID"] = (
            results_df["student_ID"]
            .astype(str)
            .apply(lambda sid: ''.join(unscramble_dict.get(char, char) for char in sid))
        )
        return results_df

    elif isinstance(input_data, str):
        return ''.join(unscramble_dict.get(char, char) for char in input_data)

    else:
        print("Input must be a pandas DataFrame or a string representing a student_ID.")
        return None
