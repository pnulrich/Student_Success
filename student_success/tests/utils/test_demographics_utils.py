import pytest
import pandas as pd
import numpy as np
from student_success.utils.demographics_utils import (
    validate_columns,
    set_up_demographic_flags,
    demographics_first_semester
)


# Core logic for validation
def validate_columns(df_columns, required_columns):
    missing_columns = [col for col in required_columns if col not in df_columns]
    if missing_columns:
        raise ValueError(f"The following required columns are missing from your dataframe: {', '.join(missing_columns)}")

# Dummy dataframe for test cases
def make_demo_df():
    return pd.DataFrame({
        'student_ID': [1, 2, 3, 4, 5],
        'demographics_term': [202101, 202101, 202101, 202101, 202101],
        'demographics_hispanic': ['Non-Hispanic', 'Hispanic', 'Non-Hispanic', 'Non-Hispanic', 'Non-Hispanic'],
        'demographics_ethnicity': [1, 2, 1, 1,1],
        'demographics_race': ['B', 'W', 'Z', 'M', 'BZ'],
        'demographics_sex': ['M', 'F', 'F', 'M', 'X'],
        'flag_first_generation': ['Y', 'N', 'Y', 'N', 'N'],
        'flag_PELL': ['Y', 'N', np.nan, 'Y', 'N'],
        'transfer_hours_term': [0, 15, 0, np.nan, 0]
    })

def test_validate_columns_success():
    cols = ['A', 'B', 'C']
    required = ['A', 'B']
    validate_columns(cols, required)  # should not raise

def test_validate_columns_failure():
    with pytest.raises(ValueError) as excinfo:
        validate_columns(['X', 'Y'], ['A', 'B'])
    assert "missing" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        validate_columns(['A', 'Y'], ['A', 'B'])
    assert "missing" in str(excinfo.value)

def test_set_up_demographic_flags_all_flags():
    df = make_demo_df()
    flagged = set_up_demographic_flags(df)
    assert all(col in flagged.columns for col in ['flag_PEER', 'flag_hispanic', 'flag_PELL', 'flag_first_generation', 'flag_sex'])
    assert flagged.loc[1, 'flag_PEER'] == 1  # Hispanic override


def test_demographics_first_semester_filtering():
    df = make_demo_df()

    result_all = demographics_first_semester(df, transfer_status="any", return_dataframe=1)
    assert len(result_all) == 5

    result_with = demographics_first_semester(df, transfer_status="with", return_dataframe=0)
    assert result_with == [2]

    result_without = demographics_first_semester(df, transfer_status="without", return_dataframe=0)
    assert set(result_without) == {1, 3, 4, 5}
