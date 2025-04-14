import pandas as pd
import pytest
from student_success.metrics.retention_flags import generate_STEM_major_retention_flag
from student_success.utils.constants import STEM_CORE_MAJORS


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'student_ID': [1, 2, 3, 4],
        'major_term_earliest': ['BIO', 'PSY', 'ENG', 'CSC'],
        'major_term': ['BIO', 'SOC', 'ENG', 'MCE'],  # last student changed majors
    })


def test_retention_flag_correct(sample_df):
    major_list = ['BIO', 'PSY', 'ENG', 'CSC']
    result = generate_STEM_major_retention_flag(sample_df, major_list=major_list, stem=False)

    # Check retention flags
    expected = [1, 0, 1, 0]  # Only students 1 and 3 retained major
    assert result['flag_retention_major'].tolist() == expected


def test_stem_flag_included(sample_df):
    major_list = ['BIO', 'PSY', 'ENG', 'CSC']
    result = generate_STEM_major_retention_flag(sample_df, major_list=major_list, stem=True)

    expected = [1 if m in STEM_CORE_MAJORS else 0 for m in result['major_term']]
    assert result['flag_retention_STEM'].tolist() == expected


def test_stem_flag_excluded(sample_df):
    result = generate_STEM_major_retention_flag(sample_df, major_list=['BIO', 'CSC'], stem=False)
    assert 'flag_retention_STEM' not in result.columns


def test_filtered_to_earliest_major(sample_df):
    # Only include BIO and CSC as target majors
    result = generate_STEM_major_retention_flag(sample_df, major_list=['BIO', 'CSC'])

    assert set(result['major_term_earliest'].unique()) == {'BIO', 'CSC'}
    assert len(result) == 2  # Should only return students 1 and 4


def test_with_custom_major_col():
    df = pd.DataFrame({
        'major_term_earliest': ['BIO', 'CSC'],
        'current_major': ['BIO', 'MCE'],
        'custom_major_column' : ['BIO', 'MCE']
    })
    result = generate_STEM_major_retention_flag(df, major_list=['BIO', 'CSC'], major_col='custom_major_column')

    assert 'flag_retention_major' in result.columns
    assert result['flag_retention_major'].tolist() == [1, 0]
    assert result['flag_retention_STEM'].tolist() == [1, 1 if 'MCE' in STEM_CORE_MAJORS else 0]
