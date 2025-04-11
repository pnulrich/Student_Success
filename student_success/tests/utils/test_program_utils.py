import numpy as np
from student_success.utils.program_utils import classify_discipline, lookup_major_name

def test_classify_discipline_known():
    assert classify_discipline('BIO') == 'Biology'
    assert classify_discipline('CSC') == 'Other STEM'
    assert classify_discipline('PSY') == 'STEM-Related'

def test_classify_discipline_unknown():
    assert classify_discipline('ENG') == 'Non-STEM'

def test_classify_discipline_nan():
    assert np.isnan(classify_discipline(np.nan))

def test_lookup_major_name_known():
    assert lookup_major_name('BIO') == 'Biology'
    assert lookup_major_name('CSC') == 'Computer Science'
    assert lookup_major_name('PSY') == 'Psychology'

def test_lookup_major_name_unknown():
    assert lookup_major_name('ENG') == 'Other'

def test_lookup_major_name_nan():
    assert np.isnan(lookup_major_name(np.nan))
