# tests/metrics/test_retention_plots.py

import pytest
import pandas as pd
from student_success.metrics.retention_plots import (
    plot_retention_rate,
    plot_cumulative_retention_rate,
    plot_major_retention_rate,
    _summarize_retention,
    _calculate_retention_stats,
    _summarize_cumulative_retention
)

@pytest.fixture
def sample_retention_df():
    return pd.DataFrame({
        'student_ID': [1, 1, 2, 2, 3, 3],
        'semester_number': [1, 2, 1, 2, 1, 2],
        'major_earliest_term': ['BIO', 'BIO', 'BIO', 'BIO', 'PSY', 'PSY'],
        'flag_retention_major': [1, 1, 1, 0, 1, 0],
        'flag_retention_STEM': [1, 1, 1, 1, 0, 0],
        'graduation_flag': [0, 1, 0, 0, 0, 0],
        'major_matriculation': ['BIO', 'BIO', 'BIO', 'BIO', 'PSY', 'PSY'],
        'flag_major_retention': [1, 1, 1, 0, 1, 0]
    })

def test_summarize_retention(sample_retention_df):
    stats = _summarize_retention(sample_retention_df, 'semester_number', 'flag_retention_major')
    assert set(['mean', 'std', 'count']).issubset(stats.columns)

def test_calculate_retention_stats(sample_retention_df):
    stats = _calculate_retention_stats(sample_retention_df, 'semester_number', 'flag_major_retention')
    assert 'retention' in stats.columns
    assert 'std_dev' in stats.columns

def test_summarize_cumulative_retention(sample_retention_df):
    stats = _summarize_cumulative_retention(sample_retention_df, 'semester_number', 'flag_retention_major', 'graduation_flag')
    assert set(['retention', 'graduation', 'leaving']).issubset(stats.columns)

def test_plot_retention_rate_runs(sample_retention_df):
    plot_retention_rate(sample_retention_df, major_list=['BIO'])

def test_plot_cumulative_retention_rate_runs(sample_retention_df):
    plot_cumulative_retention_rate(sample_retention_df, major_list=['BIO'])

def test_plot_major_retention_rate_runs(sample_retention_df):
    plot_major_retention_rate(sample_retention_df, major='BIO')
