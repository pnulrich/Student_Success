import pytest
import pandas as pd
from student_success.hazard_analysis.hazard_utils import (
    calculate_semester_interval,
    assign_outcome_indicators,
    safe_eval,
    calculate_probabilities
)

def test_calculate_semester_interval():
    assert calculate_semester_interval(202308, 202401) == 1
    assert calculate_semester_interval(202308, 202405) == 2
    assert calculate_semester_interval(202308, 202508) == 6
def test_calculate_semester_interval_invalid():
    with pytest.raises(ValueError):
        calculate_semester_interval(202308, 202305)
def test_safe_eval_success():
    assert safe_eval("{'key': 'value'}") == {'key': 'value'}
    assert safe_eval("[1, 2, 3]") == [1, 2, 3]
    assert safe_eval("42") == 42

def test_safe_eval_fail():
    assert safe_eval("invalid syntax") is None
    assert safe_eval(None) is None
    assert safe_eval(123) == 123  # already an int

def test_assign_outcome_indicators_graduation_in_major():
    row = pd.Series({
        'demographics_term': 202308,
        'flag_graduation_term': 1,
        'major_graduation': ['BIO'],
        'major_term': 'BIO'
    })
    result = assign_outcome_indicators(row, prev_major_term='BIO', term_earliest=202001, first_major='BIO', is_last_semester=True, max_demographics_term=202308)
    assert result == 2  # Graduated in first major

def test_calculate_probabilities_structure():
    df = pd.DataFrame({
        'student_ID': [1, 2, 3, 4],
        'semester_number': [1, 1, 2, 2],
        'outcome_indicator': [1, -1, 2, -1]
    })
    result = calculate_probabilities(df)
    assert set(result.keys()) == {"proportions_df", "cumulative_df", "active_student_counts"}
    assert isinstance(result['proportions_df'], pd.DataFrame)
    assert isinstance(result['cumulative_df'], pd.DataFrame)
    assert isinstance(result['active_student_counts'], pd.Series)