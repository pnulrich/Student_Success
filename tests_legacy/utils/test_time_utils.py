import pytest
import pandas as pd

from student_success.utils.time_utils import (
    adjust_grad_term, create_semesters, get_academic_year,
    get_nth_year_fall_term, increment_semester, calculate_running_semester_number
)


# ---------------------------
# Tests for adjust_grad_term
# ---------------------------
def test_adjust_grad_term_january():
    input_date = pd.Timestamp('2022-01-15')
    expected = pd.Timestamp('2022-05-15')
    assert adjust_grad_term(input_date) == expected


def test_adjust_grad_term_may():
    input_date = pd.Timestamp('2022-05-01')
    expected = pd.Timestamp('2022-08-01')
    assert adjust_grad_term(input_date) == expected


def test_adjust_grad_term_august():
    input_date = pd.Timestamp('2022-08-30')
    expected = pd.Timestamp('2022-12-30')
    assert adjust_grad_term(input_date) == expected


def test_adjust_grad_term_other_month():
    input_date = pd.Timestamp('2022-10-01')
    assert adjust_grad_term(input_date) == input_date


def test_adjust_grad_term_nat():
    assert pd.isna(adjust_grad_term(pd.NaT))


# ---------------------------
# Tests for create_semesters
# ---------------------------
def test_create_semesters_academic():
    result = create_semesters([2022, 2023])
    expected = [202108, 202201, 202205, 202208, 202301, 202305]
    assert result == expected


def test_create_semesters_calendar():
    result = create_semesters([2022, 2023], calendar_year=True)
    expected = [202201, 202205, 202208, 202301, 202305, 202308]
    assert result == expected


# ---------------------------
# Tests for get_academic_year
# ---------------------------
def test_get_academic_year_fall():
    assert get_academic_year(202308) == 2024


def test_get_academic_year_spring():
    assert get_academic_year(202301) == 2023


def test_get_academic_year_summer():
    assert get_academic_year(202305) == 2023


def test_get_academic_year_datetime():
    assert get_academic_year(pd.Timestamp('2023-05-01')) == 2023


def test_get_academic_year_invalid():
    with pytest.raises(ValueError):
        get_academic_year(202304)


# ---------------------------
# Tests for get_nth_year_fall_term
# ---------------------------
def test_get_nth_year_fall_term_default():
    input_series = pd.Series([201008, 201101, 201105])
    result = get_nth_year_fall_term(input_series)
    expected = pd.to_datetime(pd.Series([201208, 201208, 201208]).astype(str), format='%Y%m')
    pd.testing.assert_series_equal(result, expected)


def test_get_nth_year_fall_term_as_int():
    input_series = pd.Series([201008, 201101, 201105])
    result = get_nth_year_fall_term(input_series, return_as_datetime=False)
    expected = pd.Series([201208, 201208, 201208])
    pd.testing.assert_series_equal(result, expected)


# ---------------------------
# Tests for increment_semester
# ---------------------------
def test_increment_semester_spring():
    assert increment_semester(202201) == 202205


def test_increment_semester_summer():
    assert increment_semester(202205) == 202208


def test_increment_semester_fall():
    assert increment_semester(202208) == 202301


# ---------------------------
# Tests for calculate_running_semester_number
# ---------------------------
def test_calculate_running_semester_number():
    df = pd.DataFrame({
        'student_ID': ['A', 'A', 'A', 'B', 'B'],
        'demographics_term': [202201, 202205, 202208, 202201, 202208]
    })
    result = calculate_running_semester_number(df)
    expected = pd.Series([1, 2, 3, 1, 2], name='semester_number')
    pd.testing.assert_series_equal(result['semester_number'].reset_index(drop=True), expected)
