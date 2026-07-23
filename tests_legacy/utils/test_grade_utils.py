import pandas as pd
import pytest
import numpy as np

from student_success.utils.grade_utils import (
    strip_grade_suffixes,
    num_grade_institutional,
    num_grade_normalized,
    letter_grade_simplify,
    letter_grade_clean
)


@pytest.mark.parametrize("input_grade, expected_output", [
    ("A+", "A+"),
    ("A+*", "A+"),
    ("B^R", "B"),
    ("C#", "C"),
    ("D@", "D"),
    ("F%", "F"),
    ("B^R%", "B"),
    ("A", "A"),
    (None, None),
    (np.nan, "nan")  # np.nan is cast to "nan" string in some workflows
])
def test_strip_grade_suffixes(input_grade, expected_output):
    assert strip_grade_suffixes(input_grade) == expected_output


@pytest.mark.parametrize("grade, expected_numeric", [
    ("A+", 4.33), ("A", 4), ("A-", 3.67),
    ("B+", 3.33), ("B", 3), ("B-", 2.67),
    ("C+", 2.33), ("C", 2), ("C-", 1.67),
    ("D", 1), ("F", 0),
    ("C*", 2), ("D^R", 1),
    ("WM", -2), ("W", -1), ("WF", -1),
    ("S", -3), ("U", -3),
    ("IP", -2), ("GP", -2), ("GH", -2), ("I", -2),
    (None, -1), ("nan", -2),
    ("N", -2), ("V", -2),
    ("B*%", 3)
])
def test_num_grade_institutional(grade, expected_numeric):
    assert num_grade_institutional(grade) == expected_numeric


@pytest.mark.parametrize("num_grade, institutional_max, expected", [
    (4.0, 4.0, 4.0),
    (3.0, 4.0, 3.0),
    (2.5, 5.0, 2.0),
    (None, 4.0, -1),
    (4.0, None, -1),
    (4.5, 4.0, -1),
    (-1, 4.0, -1),
    (4.0, -1, -1)
])
def test_num_grade_normalized(num_grade, institutional_max, expected):
    assert num_grade_normalized(num_grade, institutional_max) == expected


def test_letter_grade_simplify_with_c_minus_flag_true():
    df = pd.DataFrame({"course_grade_letter": ["A+", "B-", "C-", "C", "D*", "D^R", "F", "W%", "WM", "IF*"]})
    simplified_df = letter_grade_simplify(df, c_minus_flag=True)
    expected = ["A", "B", "D", "C", "D", "D", "F", "W", "W", "F"]
    assert simplified_df["course_grade_letter_simp"].tolist() == expected


def test_letter_grade_simplify_with_c_minus_flag_false():
    df = pd.DataFrame({"course_grade_letter": ["A+", "B-", "C-", "C", "D*", "D^R", "F", "W%", "WM", "IF*"]})
    simplified_df = letter_grade_simplify(df, c_minus_flag=False)
    expected = ["A", "B", "C", "C", "D", "D", "F", "W", "W", "F"]
    assert simplified_df["course_grade_letter_simp"].tolist() == expected


def test_letter_grade_clean():
    df = pd.DataFrame({"course_grade_letter": ["A+*", "B^R", "C#", "D@", "F%", "A"]})
    cleaned_df = letter_grade_clean(df)
    expected = ["A+", "B", "C", "D", "F", "A"]
    assert cleaned_df["course_grade_letter"].tolist() == expected
