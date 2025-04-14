import pytest
import pandas as pd
from student_success.metrics.retention_analysis import major_retention

@pytest.fixture
def base_demographics_df():
    return pd.DataFrame({
        'student_ID': [1, 1, 2, 2, 3, 3, 4, 4],
        'demographics_term': [202101, 202102, 202101, 202102, 202101, 202102, 202101, 202102],
        'major_term': ['BIO', 'BIO', 'BIO', 'PSY', 'PSY', 'PSY', 'BIO', 'BIO'],
        'Grad_term': [0, 202102, 0, 0, 0, 0, 0, 0]
    })

# monkeypatching keeps the testing clear; we're not testing create_semsters() but want to test the retention functions directly
def create_semesters_stub(years):
    return [202101, 202102]

@pytest.mark.parametrize("major_code", ['BIO'])
def test_retention_flags_and_columns(monkeypatch, base_demographics_df, major_code):
    monkeypatch.setattr("student_success.metrics.retention_analysis.create_semesters", create_semesters_stub)
    years = [2021]
    student_ids = [1, 2, 3, 4]

    major_retention_df, major_count_df = major_retention(base_demographics_df.copy(), years, major_code, student_ids)

    # Check required columns exist
    expected_columns = {
        'student_ID', 'semester', 'AcademicYear', 'major', 'major_retention_flag',
        'grad_flag', 'grad_term', 'major_retention_flag_running', 'total_semesters'
    }
    assert expected_columns.issubset(set(major_retention_df.columns))

def test_graduation_summary(monkeypatch, base_demographics_df):
    monkeypatch.setattr("student_success.metrics.retention_analysis.create_semesters", create_semesters_stub)
    years = [2021]
    student_ids = [1, 2, 3, 4]
    major_code = 'BIO'

    _, major_count_df = major_retention(base_demographics_df.copy(), years, major_code, student_ids)

    assert 'major' in major_count_df.columns
    assert 'count' in major_count_df.columns
    assert major_count_df['count'].sum() > 0

def test_student_who_switches_majors(monkeypatch):
    data = pd.DataFrame({
        'student_ID': [5, 5, 5],
        'demographics_term': [202108, 202201, 202205],
        'major_term': ['BIO', 'BIO', 'PSY'],
        'Grad_term': [0, 0, 202103]
    })
    monkeypatch.setattr("student_success.metrics.retention_analysis.create_semesters", lambda years: [202108, 202201, 202205])
    years = [2021]
    student_ids = [5]
    major_code = 'BIO'

    major_retention_df, _ = major_retention(data.copy(), years, major_code, student_ids)

    change_row = major_retention_df.loc[major_retention_df['student_ID'] == 5]
    assert change_row['major_change_semester'].notna().any()
    assert change_row['semesters_before_major_change'].max() == 2
