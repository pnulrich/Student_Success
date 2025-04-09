# Mapping for descriptions of race
PEER_DESCRIPTION_DICT = {
    'American Indian or Alaska Native': 1, 'Asian': 0, 'Black or African American': 1,
    'More Than One Race Reported': 2, 'Not Reported': -1, 'White': 0, 'Pacific Islander': 1,
    'Native Hawaiian or Pacific Islander': 1
}

# Mapping for abbreviated race codes
PEER_ABBREVIATION_DICT = {
    'B': 'Black or African American', 'W': 'White', 'Z': 'Asian',
    'P': 'Pacific Islander', 'I': 'American Indian or Alaska Native',
    'H': 'Hispanic', 'N': 'Not Reported', 'M': 'More Than One Race Reported'
}

# Mapping for descriptions of sex
SEX_DICT = {'Female': 1, 'Male': 0, 'F': 1, 'M': 0}

# dictionary map for disciplinary categories
# Users may modify or expand this dictionary based on their research questions or academic programs.
DISCIPLINE_DICT = {
    'BNUR': 'STEM-Related',
    'BIO': 'Biology',
    'EXS': 'Other STEM',
    'IDS': 'Interdisciplinary Studies',
    'NEUR': 'Other STEM',
    'CHM': 'Other STEM',
    'PHY': 'Other STEM',
    'GEOS': 'Other STEM',
    'MTH': 'Other STEM',
    'GLY': 'Other STEM',
    'GEO': 'Other STEM',
    'GEOL': 'Other STEM',
    'GEOP': 'Other STEM',
    'CSC': 'Other STEM',
    'CSCI': 'Other STEM',
    'PSY': 'STEM-Related'
}

# dictionary map for major abbreviations
# Users may modify or expand this dictionary based on their research questions or academic programs.
MAJORS_DICT = {
    'BNUR': 'Nursing',
    'BIO': 'Biology',
    'EXS': 'Exercise Science',
    'IDS': 'Interdisciplinary Studies',
    'NEUR': 'Neuroscience',
    'CHM': 'Chemistry',
    'PHY': 'Physics',
    'GEOS': 'Geosciences',
    'MTH': 'Mathematics',
    'GLY': 'Geology',
    'GEO': 'Geosciences',
    'GEOL': 'Geology',
    'GEOP': 'Geology',
    'CSC': 'Computer Science',
    'CSCI': 'Computer Science',
    'PSY': 'Psychology'
}