import pandas as pd
import pytest
from institutionaldata.utils.matriculation_utils import (
    filter_by_valid_matriculation_term,
    clean_and_adjust_matriculation
)

# Sample dataset
@pytest.fixture
def demo_df():
    return pd.DataFrame({
        'student_ID': [1, 1, 2, 2, 3],
        'matriculation_term': [202001, 202001, 202001, 202008, 201901],
        'demographics_term': [202001, 202101, 202001, 202008, 201905]
    })

def test_filter_by_valid_matriculation_term(demo_df):
    result = filter_by_valid_matriculation_term(demo_df)
    # Should only include students who have at least one matching row
    assert set(result['student_ID']) == {1, 2}

    # Each included student must have at least one row where demographics_term == matriculation_term
    grouped = result[result['demographics_term'] == result['matriculation_term']].groupby('student_ID')
    assert set(grouped.groups.keys()) == {1, 2}

def test_filter_missing_columns():
    with pytest.raises(ValueError):
        filter_by_valid_matriculation_term(pd.DataFrame({
            'student_ID': [1], 'matriculation_term': [202001]
        }))

def test_clean_and_adjust_include_all(demo_df):
    result = clean_and_adjust_matriculation(demo_df, include_multiple_matriculations=1)
    assert 'matriculation_term_adjusted' in result.columns
    assert all(result['matriculation_term_adjusted'].notna())
    assert result[result['student_ID'] == 3]['matriculation_term_adjusted'].iloc[0] == 201905

def test_clean_and_adjust_exclude_multi(demo_df):
    modified_df = demo_df.copy()
    modified_df.loc[2, 'matriculation_term'] = 202004  # student 2 now has two different matriculations
    result = clean_and_adjust_matriculation(modified_df, include_multiple_matriculations=0)
    assert 2 not in result['student_ID'].unique()

def test_clean_and_adjust_with_range_filter(demo_df):
    result = clean_and_adjust_matriculation(demo_df, demographics_range_min=202001)
    assert result['matriculation_term_min'].min() >= 202001
    assert result['matriculation_term_adjusted'].min() >= 202001
