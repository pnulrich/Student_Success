import ast
import pandas as pd
def validate_columns(df_columns, required_columns):
    """
    Validates that all required columns are present in a DataFrame.

    Parameters
    ----------
    df_columns : iterable
        A list-like object (e.g., df.columns) containing the column names from a DataFrame.
    required_columns : list of str
        A list of column names expected to be present in the DataFrame.

    Raises
    ------
    ValueError
        If any of the required columns are missing, a ValueError is raised listing them.
    """

    missing_columns = []
    for column in required_columns:
        if column not in df_columns:
            missing_columns.append(column)
    if len(missing_columns) > 0:
        raise ValueError(f"The following required columns are missing from your dataframe: {', '.join(missing_columns)}")

# def safe_parse_tuple(val):
#     """
#     Robustly parses list/tuple-like values from strings or native sequences,
#     removing blank, null, and 'nan' values regardless of type.
#     """
#     if isinstance(val, (list, tuple)):
#         return [
#             str(x).strip() for x in val
#             if (not isinstance(x, float) or pd.notna(x)) and
#                str(x).strip().lower() not in {'', 'nan', 'none'}
#         ]
#
#     if isinstance(val, str):
#         try:
#             return list(ast.literal_eval(val))
#         except (ValueError, SyntaxError):
#             items = val.strip("() ").split(",")
#             return [
#                 x.strip().strip("'\"") for x in items
#                 if x.strip().lower() not in {'', 'nan', 'none'}
#             ]
#
#     return []

# def safe_parse_tuple(val):
#     """
#     Robustly parses list/tuple-like values from strings or native sequences,
#     removing blank, null, and 'nan' values regardless of type.
#
#     Always returns a clean list of strings.
#     """
#     # Normalize all inputs to a list of strings
#     if pd.isna(val) or val in ['', 'nan', 'None']:
#         return []
#
#     # Step 1: Convert to a string representation, remove parentheses
#     val_str = str(val).strip("() ")
#     items = val_str.split(",")
#
#     # Step 2: Clean and filter
#     clean_parts = []
#     for item in items:
#         s = str(item).strip().strip("'\"").lower()
#         if s not in {'', 'nan', 'none'}:
#             clean_parts.append(item.strip().strip("'\""))
#
#     return clean_parts

# Redefine the updated safe_parse_tuple function
def safe_parse_tuple(val):
    """
    Robustly parses list/tuple-like values from strings or native sequences,
    preserving structure and replacing invalid entries (e.g., NaN, None) with None.

    Parameters:
        val (str | tuple | list): Input to parse.

    Returns:
        list: List of parsed values, preserving positional structure.
    """
    # Case 1: Already a tuple or list
    if isinstance(val, (list, tuple)):
        return [
            x if pd.notna(x) and str(x).strip().lower() not in {'', 'nan', 'none'}
            else None
            for x in val
        ]

    # Case 2: String input – try literal_eval first
    if isinstance(val, str):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, (list, tuple)):
                return [
                    x if pd.notna(x) and str(x).strip().lower() not in {'', 'nan', 'none'}
                    else None
                    for x in parsed
                ]
        except (ValueError, SyntaxError):
            # Fallback to manual split
            items = val.strip("() ").split(",")
            return [
                x.strip().strip("'\"") if x.strip().lower() not in {'', 'nan', 'none'} else None
                for x in items
            ]

    # Case 3: Fallback
    return []