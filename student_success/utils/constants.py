# student_success/utils/program_utils.py

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


# major codes grouped by discipline
MAJORS_DISCIPLINES = {
    'bio_sci' : ['BIO', 'NEUR'],
    'phy_sci' : ['CHM', 'PHY', 'GEOS', 'MTH', 'GLY', 'GEO', 'GEOL'],
    'eng_CS' : ['CSC', 'PCSC', 'MCE', 'CSCI'],
    'other_STEM' : [
        'PSY', 'PCIS', 'CIS', 'PH', 'EDUC', 'ECON', 'AN', 'NTR', 'NTRS', 'PTH', 'AC', 'EXS', 'ECE', 'FI', 'DSC', 'DSCI', 'PDSC',
        'BUE', 'HPE', 'MGRS', 'NUTR', 'BNUR', 'PNUR', 'GPY', 'BUAN', 'NUR', 'NURN', 'NURL', 'CBE', 'IEML', 'SEE', 'SOC', 'WGSS',
        'SPE', 'GDS', 'AED', 'ALG', 'AS', 'AVI', 'BRF', 'CJ', 'DHYG', 'ELE', 'ENI', 'FMV', 'GDV', 'GER', 'IS', 'MLE', 'MGT',
        'MID', 'MK', 'MHA', 'MT', 'ML', 'PAC', 'PAS', 'PBUE', 'PBRF', 'PECE', 'PENI', 'PFMN', 'PFMV', 'PFI', 'PGDV', 'PHPE', 'PML',
        'PMGT', 'PNTR', 'PMK', 'PPSY', 'PPH', 'PRMI', 'PREA', 'PSPE', 'PSW', 'PUP', 'RE', 'RMI', 'RTP', 'SS', 'SW', 'UPS', 'UST', 'WST',
        'HOS', 'HUR', 'POL', 'RT'],
    'undeclared' : ['0000', '0001', '000P', '00GP', 'Undeclared', 'Exploratory']
}

STEM_CORE_DISCIPLINE_CATEGORIES = ['bio_sci', 'phy_sci', 'eng_CS']
ALL_DISCIPLINE_CATEGORIES = list(MAJORS_DISCIPLINES.keys())
STEM_CORE_MAJORS = MAJORS_DISCIPLINES['bio_sci'] + MAJORS_DISCIPLINES['phy_sci'] + MAJORS_DISCIPLINES['eng_CS']

# Flattened lookup, associating all majors with respective disciplines
MAJOR_TO_DISCIPLINE_DICT = {
    major: discipline
    for discipline, majors in MAJORS_DISCIPLINES.items()
    for major in majors
}

DISCIPLINE_LABELS = {
    'bio_sci': 'Biological Sciences',
    'phy_sci': 'Physical Sciences',
    'eng_CS': 'Engineering and Computer Science',
    'other_STEM': 'Other STEM Fields',
    'undeclared': 'Undeclared'
}

PREMAJOR_TO_MAJOR_DICT = {
    'PAC': 'AC',
    'PAS': 'AS',
    'PBRF': 'BRF',
    'PBUE': 'BUE',
    'PCIS': 'CIS',
    'PCSC': 'CSC',
    'PDSC': 'DSCI',
    'PECE': 'ECE',
    'PENI': 'ENI',
    'PEXS': 'EXS',
    'PFI': 'FI',
    'PFMM': 'FMM',
    'PGDV': 'GDV',
    'PHOS': 'HOS',
    'PHPE': 'HPE',
    'PIDS': 'IDS',
    'PJOU': 'JOU',
    'PMGR': 'MGRS',
    'PMGT': 'MGT',
    'PMK': 'MK',
    'PML': 'ML',
    'PNTR': 'NTR',
    'PNUR': 'NUR',
    'PPH': 'PH',
    'PPSY': 'PSY',
    'PREA': 'RE',
    'PRMI': 'RMI',
    'PSLI': 'SLI',
    'PSPE': 'SPE',
    'PSW': 'SW',
}

# reverse lookup of PREMAJORS
MAJOR_TO_PREMAJOR_DICT = {
    v: [k for k, val in PREMAJOR_TO_MAJOR_DICT.items() if val == v]
    for v in set(PREMAJOR_TO_MAJOR_DICT.values())
}

# dictionary map for major abbreviations
# Users may modify or expand this dictionary based on their research questions or academic programs.
MAJOR_ABBREV_TO_LABEL = {
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

# -------------------------------------------------------------------
# Retention Outcome Classification
# -------------------------------------------------------------------

RETENTION_OUTCOME_LABELS = [
    'still_enrolled',    # 0: Active in original major
    'left_major',        # 1: Changed major
    'left_university',   # 2: Inactive and not graduated
    'graduated'          # 3: Completed degree
]

RETENTION_OUTCOME_CODE_DICT = {
    'still_enrolled': 0,
    'left_major': 1,
    'left_university': 2,
    'graduated': 3
}

RETENTION_OUTCOME_LABEL_DICT = {v: k for k, v in RETENTION_OUTCOME_CODE_DICT.items()}

