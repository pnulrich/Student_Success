"""
Centralized constant definitions for classification, labeling, and visualization in the student_success package.

This module includes dictionaries and lists used across modules to:
- Categorize and label majors and disciplines.
- Map demographic flags to colors for plotting.
- Provide lookup tables for major and pre-major codes.
- Define retention outcome labels and codes.
- Support visual grouping and color mapping for Sankey diagrams.

Usage Notes for Institutional Customization
-------------------------------------------
Most values in this module can and should be customized to reflect your institution's specific academic codes
and demographic categorizations. You may wish to:

- Update `MAJORS_DISCIPLINES` to match your institution’s internal major abbreviations.
- Edit `PREMAJOR_TO_MAJOR_DICT` and `MAJOR_ABBREV_TO_LABEL` if your institution uses different codes for pre-majors or official program names.
- Adjust `PEER_DESCRIPTION_DICT`, `SEX_DICT`, and `DEMOGRAPHIC_COLOR_MAPS` to reflect how your student information system encodes race, gender, and first-gen status.
- Modify `SANKEY_DISCIPLINE_GROUPS` and `SANKEY_DISCIPLINE_COLOR_MAP` to simplify and recolor degree pathways in visualizations.
- Add or remove entries in `RETENTION_OUTCOME_*` variables if you use different terminology or need additional categories.

To avoid breaking functions that rely on these constants, make edits carefully and test your visualizations or classification outputs after each change.

Contents
--------
- PEER_ABBREVIATION_DICT, PEER_DESCRIPTION_DICT: Mappings for racial/ethnic group codes and classifications.
- SEX_DICT: Mapping of gender identifiers to binary flags.
- DEMOGRAPHIC_COLOR_MAPS: Color schemes for demographic group visualizations.
- MAJORS_DISCIPLINES, STEM_CORE_MAJORS: Groupings of major codes by academic discipline.
- MAJOR_TO_DISCIPLINE_DICT, DISCIPLINE_LABELS: Discipline-level lookups and labels.
- PREMAJOR_TO_MAJOR_DICT, MAJOR_TO_PREMAJOR_DICT: Pre-major and major abbreviation crosswalks.
- MAJOR_ABBREV_TO_LABEL: Readable labels for major abbreviations.
- RETENTION_OUTCOME_LABELS, RETENTION_OUTCOME_CODE_DICT, RETENTION_OUTCOME_LABEL_DICT: Encodings and labels for retention and graduation status.
- SANKEY_DISCIPLINE_GROUPS, SANKEY_DISCIPLINE_COLOR_MAP: Simplified groupings and colors for Sankey plot visualization.
"""

GRADE_SIMPLIFICATION_MAP = {
    "A+": "A", "A": "A", "A-": "A",
    "B+": "B", "B": "B", "B-": "B",
    "C+": "C", "C": "C",
    "C-": "C",  # utils.grade_utils.letter_grade_simplify() will override to "D" during runtime if c_minus_flag=True
    "D+": "D", "D": "D", "D-": "D",
    "F": "F", "F": "F", "IF": "F", "UF": "F",
    "W": "W", "-W": "W", "WM": "W", "PW": "W", "WF":"W"
}


LETTER_GRADE_GPA_MAP = {
    "A+": 4.33, "A": 4, "A-": 3.67,
    "B+": 3.33, "B": 3, "B-": 2.67,
    "C+": 2.33, "C": 2, "C-": 1.67,
    "D": 1,
    "F": 0,
    "PW": -1,  # withdrawal
    "W": -1,  # withdrawal
    "WF": -1,  # withdrawal with failure
    "WM": -2,  # military withdrawal; treated as distinct from standard withdrawal
    "IP": -2,  # in progress
    "GP": -2,  # grade pending
    "GH": -2,  # grade hold
    "I": -2,  # incomplete
    "V": -2,  # audit
    "AU": -2,  # audit
    "N": -2,  # continuing ed
    "NR": -2,  # not reported (BS and associates level)
    "S": -3,  # satifactory (pass / fail course)
    "U": -3  # unsatisfactory (pass / fall course)
}


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

DEMOGRAPHIC_COLOR_MAPS = {
    "flag_sex": {1: "green", 0: "blue"},  # 1 = female, 0 = male
    "flag_PELL": {1: "green", 0: "blue"},  # 1 = Pell-eligible, 0 = not Pell-eligible
    "flag_first_generation": {1: "green", 0: "blue"},  # 1 = first gen, 0 = continuing gen
    "flag_PEER": {1: "brown", 0: "white"},  # 1 = PEER student, 0 = non-PEER
    "flag_hispanic": {1: "brown", 0: "white"},  # 1 = Hispanic, 0 = non-Hispanic
    "flag_grad": {1: "green", 0: "blue"}  # 1 = graduated, 0 = not graduated
}

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
    'PSY': 'Psychology',
    'NUR': 'Nursing'
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

# -------------------------------------------------------------------
# Sankey Plot Discipline Simplification (for visualization clarity)
# -------------------------------------------------------------------

SANKEY_DISCIPLINE_GROUPS = {
    'BIO': 'Target Major',
    'NEUR': 'STEM-Related',
    'CHM': 'Other STEM',
    'CSC': 'STEM-Related',
    'PSY': 'Non-STEM',
    'IDS': 'Interdisciplinary Studies',
    'NUR': 'Non-STEM',
    # Add others as needed
}

SANKEY_DISCIPLINE_COLOR_MAP = {
    'Target Major': "#88CCEE",
    'STEM-Related': "#117733",
    'Other STEM': "#DDCC77",
    'Non-STEM': "#44AA99",
    'Interdisciplinary Studies': "#888888",
    'Graduated Other': "#882255",
    'Graduated BIO': "#332288",   # dynamically injected for different target majors
    'Left College': "#CC6677",
    'Unknown': "#999999"
}

SEMESTER_NUMERIC_CODES = {
    'spring': 1,
    'summer': 5,
    'fall': 8,
    'spring_only': 2,
    'summer_only': 3,
    'spring+summer': 4,
}