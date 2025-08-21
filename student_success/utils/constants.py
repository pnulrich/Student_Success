"""
constants.py

Centralized definitions for classification, labeling, and visualization
in the student_success package.

This module provides dictionaries and lookup tables that standardize:
- Grade conversions and GPA mappings.
- Demographic group encodings and visualization colors.
- Major and discipline categorizations.
- Pre-major and major crosswalks.
- Retention outcome codes and labels.
- Simplified discipline groupings and color schemes for Sankey diagrams.

Institutional Customization
---------------------------
Most constants should be customized to reflect your institution’s codes
and conventions. Common areas for modification include:

- Majors and Disciplines:
  Update `MAJORS_DISCIPLINES`, `PREMAJOR_TO_MAJOR_DICT`, and
  `MAJOR_ABBREV_TO_LABEL` to match local major codes and program names.
- Demographics:
  Edit `PEER_DESCRIPTION_DICT`, `SEX_DICT`, and `DEMOGRAPHIC_COLOR_MAPS`
  if your student information system uses different encodings.
- Visualization:
  Adjust `SANKEY_DISCIPLINE_GROUPS` and `SANKEY_DISCIPLINE_COLOR_MAP`
  to simplify degree pathways or recolor categories in figures.
- STEM Core Categories:
  Modify `STEM_CORE_DISCIPLINE_CATEGORIES` if your institution or research question defines
  STEM categories differently.
  (Note: `ALL_DISCIPLINE_CATEGORIES` is an internal helper and should
  not be edited.)

Pitfalls
--------
- Constants are imported throughout the package. Breaking a mapping here
  (e.g., removing a key still referenced by another function) will cause
  errors downstream.
- Test analyses or plots after making changes to confirm that labels and
  groupings render as expected.

Binary Filtering Constants
--------------------------
Some constants are used in binary filters throughout the package (e.g.,
SEX_DICT, PEER_DESCRIPTION_DICT, demographic flag mappings).

- Keys: Must match the codes used by your student information system (SIS).
- Values: Must remain binary (0 or 1) to preserve filtering logic.
- Do not add new key-value pairs or introduce additional categories unless you
  also update the filtering functions that consume these constants.
- Special cases (e.g., non-binary sex codes or additional race categories)
  require extending the package logic, not just editing the constants.

Contents
--------
- GRADE_SIMPLIFICATION_MAP, LETTER_GRADE_GPA_MAP : Grade conversion and GPA lookup.
- PEER_ABBREVIATION_DICT, PEER_DESCRIPTION_DICT : Race/ethnicity codes and descriptions.
- SEX_DICT, DEMOGRAPHIC_COLOR_MAPS : Gender and demographic encodings with color maps.
- MAJORS_DISCIPLINES, STEM_CORE_MAJORS : Groupings of majors into discipline categories.
- STEM_CORE_DISCIPLINE_CATEGORIES : Editable list of discipline categories designated as STEM core.
- MAJOR_TO_DISCIPLINE_DICT, DISCIPLINE_LABELS : Discipline lookup tables.
- PREMAJOR_TO_MAJOR_DICT, MAJOR_TO_PREMAJOR_DICT : Pre-major ↔ major crosswalks.
- MAJOR_ABBREV_TO_LABEL : Readable program labels.
- RETENTION_OUTCOME_LABELS, RETENTION_OUTCOME_CODE_DICT, RETENTION_OUTCOME_LABEL_DICT : Retention/graduation codes.
- SANKEY_DISCIPLINE_GROUPS, SANKEY_DISCIPLINE_COLOR_MAP : Simplified groupings and color assignments for Sankey plots.
- SEMESTER_NUMERIC_CODES : Standardized numeric codes for academic terms.
"""

# Keys (the first item in each pair): Fixed grade codes from your student information system (SIS) – do not change.
# Values (the second item in each pair): Safe to adjust mappings (e.g., GPA values, simplification categories).
# Caution: if your SIS uses different conventions, you may need to add key/value pairs or make adjustments. Remember to
# test thoroughly.
GRADE_SIMPLIFICATION_MAP = {
    "A+": "A",
    "A": "A",
    "A-": "A",
    "B+": "B",
    "B": "B",
    "B-": "B",
    "C+": "C",
    "C": "C",
    "C-": "C",  # utils.grade_utils.letter_grade_simplify() will override to "D" during runtime if c_minus_flag=True
    "D+": "D",
    "D": "D",
    "D-": "D",
    "F": "F",
    "IF": "F",
    "UF": "F",
    "W": "W",
    "-W": "W",
    "WM": "W",
    "PW": "W",
    "WF": "W"
}

# Keys (content before colon): Fixed grade codes from your student information system (SIS). Change grade codes with caution
# and test code output thoroughly upon implementation.
# Values (content after colon ): It is safe to change any value except those that are negative. Do not adjust
# negative values - these are critical for filtering steps critical in package functions.
LETTER_GRADE_GPA_MAP = {
    "A+": 4.33,
    "A": 4,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2,
    "C-": 1.67,
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
    "S": -3,  # satisfactory (pass / fail course)
    "U": -3  # unsatisfactory (pass / fall course)
}


# Mapping for descriptions of race
# Keys: Race/ethnicity descriptions from your student information system (SIS).
# Values: Binary encodings used for PEER filtering.
# 0 = non-PEER, 1 = PEER, 2 = multi-race, -1 = not reported.
# Do not add new categories without updating the filtering logic.
PEER_DESCRIPTION_DICT = {
    'American Indian or Alaska Native': 1,
    'Asian': 0,
    'Black or African American': 1,
    'More Than One Race Reported': 2,
    'Not Reported': -1,
    'White': 0,
    'Pacific Islander': 1,
    'Native Hawaiian or Pacific Islander': 1
}

# Mapping for abbreviated race codes to descriptions used in your student information system (SIS)
# Keys (content before colon): Institution-provided demographic codes.
# Values (content after colon): Safe to adjust if your institutional coding differs.
PEER_ABBREVIATION_DICT = {
    'B': 'Black or African American',
    'W': 'White',
    'Z': 'Asian',
    'P': 'Pacific Islander',
    'I': 'American Indian or Alaska Native',
    'H': 'Hispanic',
    'N': 'Not Reported',
    'M': 'More Than One Race Reported'
}

# Mapping for descriptions of sex
# Keys: SIS codes for sex (must match your institution’s values).
# Values: Binary encodings used in filters. Do not add or change beyond 0/1
# unless you also modify downstream functions. Non-binary categories require
# extending the filtering logic in student_success.
SEX_DICT = {
    'Female': 1,
    'Male': 0,
    'F': 1,
    'M': 0}

# colors used in figures for visualization can be modified freely. Note that changes to the various mappings above may
# require additions or changes to the map values between the curly brackets
DEMOGRAPHIC_COLOR_MAPS = {
    "flag_sex": {1: "green", 0: "blue"},  # 1 = female, 0 = male
    "flag_PELL": {1: "green", 0: "blue"},  # 1 = Pell-eligible, 0 = not Pell-eligible
    "flag_first_generation": {1: "green", 0: "blue"},  # 1 = first gen, 0 = continuing gen
    "flag_PEER": {1: "brown", 0: "white"},  # 1 = PEER student, 0 = non-PEER
    "flag_hispanic": {1: "brown", 0: "white"},  # 1 = Hispanic, 0 = non-Hispanic
    "flag_grad": {1: "green", 0: "blue"}  # 1 = graduated, 0 = not graduated
}

# major codes grouped by discipline
# Keys: Discipline categories – may be modified/renamed if your institution defines categories differently.
# Values: Lists of major codes – customize freely to match your student information system (SIS).
MAJORS_DISCIPLINES = {
    'bio_sci': ['BIO', 'NEUR'],
    'phy_sci': ['CHM', 'PHY', 'GEOS', 'MTH', 'GLY', 'GEO', 'GEOL'],
    'eng_CS': ['CSC', 'PCSC', 'MCE', 'CSCI'],
    'other_STEM': [
        'PSY', 'PCIS', 'CIS', 'PH', 'EDUC', 'ECON', 'AN', 'NTR', 'NTRS', 'PTH', 'AC', 'EXS', 'ECE', 'FI', 'DSC', 'DSCI', 'PDSC',
        'BUE', 'HPE', 'MGRS', 'NUTR', 'BNUR', 'PNUR', 'GPY', 'BUAN', 'NUR', 'NURN', 'NURL', 'CBE', 'IEML', 'SEE', 'SOC', 'WGSS',
        'SPE', 'GDS', 'AED', 'ALG', 'AS', 'AVI', 'BRF', 'CJ', 'DHYG', 'ELE', 'ENI', 'FMV', 'GDV', 'GER', 'IS', 'MLE', 'MGT',
        'MID', 'MK', 'MHA', 'MT', 'ML', 'PAC', 'PAS', 'PBUE', 'PBRF', 'PECE', 'PENI', 'PFMN', 'PFMV', 'PFI', 'PGDV', 'PHPE', 'PML',
        'PMGT', 'PNTR', 'PMK', 'PPSY', 'PPH', 'PRMI', 'PREA', 'PSPE', 'PSW', 'PUP', 'RE', 'RMI', 'RTP', 'SS', 'SW', 'UPS', 'UST', 'WST',
        'HOS', 'HUR', 'POL', 'RT'],
    'undeclared': ['0000', '0001', '000P', '00GP', 'Undeclared', 'Exploratory']
}

# Lists of discipline categories.
# Safe to edit STEM_CORE_DISCIPLINE_CATEGORIES.
# DO NOT edit ALL_DISCIPLINE_CATEGORIES (internal consistency required).
STEM_CORE_DISCIPLINE_CATEGORIES = ['bio_sci', 'phy_sci', 'eng_CS']
ALL_DISCIPLINE_CATEGORIES = list(MAJORS_DISCIPLINES.keys())
STEM_CORE_MAJORS = MAJORS_DISCIPLINES['bio_sci'] + MAJORS_DISCIPLINES['phy_sci'] + MAJORS_DISCIPLINES['eng_CS']

# Flattened lookup, associating all majors with respective disciplines
# Auto-generated – DO NOT edit manually.
# Update `MAJORS_DISCIPLINES` instead; this will update this mapping automatically.
MAJOR_TO_DISCIPLINE_DICT = {
    major: discipline
    for discipline, majors in MAJORS_DISCIPLINES.items()
    for major in majors
}

# Keys: Discipline category names – must match keys in MAJORS_DISCIPLINES.
# Values: Safe to adjust (human-readable labels).
DISCIPLINE_LABELS = {
    'bio_sci': 'Biological Sciences',
    'phy_sci': 'Physical Sciences',
    'eng_CS': 'Engineering and Computer Science',
    'other_STEM': 'Other STEM Fields',
    'undeclared': 'Undeclared'
}

# Keys: Pre-major codes – safe to customize to your institution.
# Values: Target major codes – must match official major abbreviations.
# Note: MAJOR_TO_PREMAJOR_DICT is auto-generated, do not edit directly.
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
# Note: MAJOR_TO_PREMAJOR_DICT is auto-generated, do not edit directly.
MAJOR_TO_PREMAJOR_DICT = {
    v: [k for k, val in PREMAJOR_TO_MAJOR_DICT.items() if val == v]
    for v in set(PREMAJOR_TO_MAJOR_DICT.values())
}

# dictionary map for major abbreviations
# Keys: Major abbreviations – must align with student information system (SIS) codes.
# Values: Safe to adjust (human-readable program labels).
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

# must remain unchanged (referenced in code)
RETENTION_OUTCOME_LABELS = [
    'still_enrolled',    # 0: Active in original major
    'left_major',        # 1: Changed major
    'left_university',   # 2: Inactive and not graduated
    'graduated'          # 3: Completed degree
]

# must remain unchanged (referenced in code)
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

# SANKEY_DISCIPLINE_GROUPS is used to "bundle" groups of disciplines into categories. The defaults use Biology as a
# focal major and STEM vs. non-STEM or related groups as an example. However, this framework is adaptable to your needs.
# Keys: Major abbreviations – safe to adjust to include additional majors.
# Values: Simplified grouping labels – safe to customize.
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

# Keys: Simplified discipline labels – must match SANKEY_DISCIPLINE_GROUPS values.
# Values: Safe to adjust (color hex codes).
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

# Keys: Term descriptors – do not change unless your SIS uses different names.
# Values: Numeric encodings – safe to adjust if your institution encodes terms differently.
SEMESTER_NUMERIC_CODES = {
    'spring': 1,
    'summer': 5,
    'fall': 8,
    'spring_only': 2,
    'summer_only': 3,
    'spring+summer': 4,
}
