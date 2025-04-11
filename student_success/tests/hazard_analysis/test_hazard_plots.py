import pandas as pd
import pytest

from student_success.hazard_analysis.hazard_plots import (
    prepare_course_heatmap_data,
)

# Define test data
@pytest.fixture
def mock_filtered_df():
    return pd.DataFrame({
        'student_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'academic_year': [2020, 2020, 2020, 2021, 2021, 2021, 2021, 2021, 2021],
        'major_term': ['BIO', 'BIO', 'BIO', 'BIO', 'BIO', 'BIO', 'PSY', 'BIO', 'BIO'],
        'course_list': [
            ['BIO1010', 'BIO2010'],
            ['BIO1010', 'BIO2020'],
            ['BIO1020'],
            ['BIO2010', 'BIO3010'],
            ['BIO2030'],
            ['BIO2020'],
            ['BIO2020', 'PSY3542'],
            ['BIO2020', 'PSY3542'],
            ['BIO1011']
        ],
        'semester_number': [1, 1, 1, 2, 2, 2, 3, 3, 3]
    })

# Test case: verify structure and output
def test_prepare_course_heatmap_data_basic(mock_filtered_df):
    result = prepare_course_heatmap_data(
        filtered_df=mock_filtered_df,
        target_major='BIO',
        min_academic_year=2020,
        max_academic_year=2021,
        number_top_courses=2,
        minimum_student_number=1,
        minimum_proportion_active_students=0.01
    )
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {'course_list', 'semester_number', 'proportion', 'frequency'}
    assert not result.empty

# Test case: verify structure and output
def test_prepare_course_heatmap_target_major(mock_filtered_df):
    result = prepare_course_heatmap_data(
        filtered_df=mock_filtered_df,
        target_major='PSY',
        min_academic_year=2000,
        max_academic_year=2041,
        number_top_courses=2,
        minimum_student_number=1,
        minimum_proportion_active_students=0.01
    )
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {'course_list', 'semester_number', 'proportion', 'frequency'}
    assert result['course_list'].tolist() == ['BIO2020', 'PSY3542']

# Test case: stricter filters result in fewer or no rows
def test_prepare_course_heatmap_data_minimum_proportion(mock_filtered_df):
    result = prepare_course_heatmap_data(
        filtered_df=mock_filtered_df,
        target_major='BIO',
        min_academic_year=2020,
        max_academic_year=2021,
        number_top_courses=2,
        minimum_student_number=1,  # deliberately low to focus on proportion
        minimum_proportion_active_students=0.9
    )
    assert result.empty

def test_prepare_course_heatmap_data_minimum_student_number(mock_filtered_df):
    result = prepare_course_heatmap_data(
        filtered_df=mock_filtered_df,
        target_major='BIO',
        min_academic_year=2020,
        max_academic_year=2021,
        number_top_courses=2,
        minimum_student_number=10,  # deliberately strict
        minimum_proportion_active_students=0.001
    )
    assert result.empty

# Test case: filter by academic year range
def test_prepare_course_heatmap_data_year_filter(mock_filtered_df):
    result = prepare_course_heatmap_data(
        filtered_df=mock_filtered_df,
        target_major='BIO',
        min_academic_year=2021,
        max_academic_year=2021,
        number_top_courses=2,
        minimum_student_number=1,
        minimum_proportion_active_students=0.001
    )
    assert set(result['semester_number']) == {2,3}  # Only semester 2 should remain
