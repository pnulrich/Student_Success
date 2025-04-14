import numpy as np
import pandas as pd
from student_success.utils.program_utils import classify_discipline, lookup_major_name

def test_classify_discipline():
    assert classify_discipline('BIO') == 'bio_sci'
    assert classify_discipline('CHM') == 'phy_sci'
    assert classify_discipline('CSC') == 'eng_CS'
    assert classify_discipline('EXS') == 'other_STEM'
    assert classify_discipline('0001') == 'undeclared'
    assert classify_discipline('HIST') == 'non_STEM'
    assert classify_discipline('ENG') == 'non_STEM'
    assert pd.isna(classify_discipline(np.nan))

def test_lookup_major_name_known():
    assert lookup_major_name('BIO') == 'Biology'
    assert lookup_major_name('CSC') == 'Computer Science'
    assert lookup_major_name('PSY') == 'Psychology'

def test_lookup_major_name_unknown():
    assert lookup_major_name('ENG') == 'Other'

def test_lookup_major_name_nan():
    assert np.isnan(lookup_major_name(np.nan))
