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