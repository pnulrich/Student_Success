"""
Utility functions for data wrangling and processing in student_success.

Submodules included:
- io_utils: Tools for file I/O, including column renaming from codebooks.
- scrambler: Functions for anonymizing and restoring student IDs.
- program_utils: Functions for metadata assignment, labeling, and lookup of information associated with majors and programs
- grade_utils: functions for manipulation and cleaning of grade columns
- grades, time_utils, matriculation, etc.: Additional support modules.
"""

from .validation import (
    validate_columns,
    safe_parse_tuple
)

from .demographics_utils import (
    set_up_demographic_flags,
    demographics_first_semester
)

from .grade_utils import (
    num_grade_normalized,
    num_grade_institutional,
    letter_grade_clean,
    letter_grade_simplify,
    filter_valid_letter_grades
)

from .io_utils import (
    load_grades,
    rename_columns_in_bulk,
    extract_column_mapping,
    flatten_column_mapping,
    concatenate_csv_files
)

from .matriculation_utils import (
    filter_by_valid_matriculation_term,
    clean_and_adjust_matriculation,
)

from .program_utils import (
    classify_discipline,
    lookup_major_name
)

from .scrambler import (
    scramble_ID,
    unscramble_ID
)

from .constants import (
    MAJOR_TO_DISCIPLINE_DICT,
    MAJOR_ABBREV_TO_LABEL,
    MAJORS_DISCIPLINES,
    MAJOR_TO_PREMAJOR_DICT,
    PREMAJOR_TO_MAJOR_DICT,
    STEM_CORE_MAJORS,
    SEX_DICT,
    PEER_ABBREVIATION_DICT,
    PEER_DESCRIPTION_DICT,
    STEM_CORE_DISCIPLINE_CATEGORIES,
    ALL_DISCIPLINE_CATEGORIES,
    DISCIPLINE_LABELS,
    RETENTION_OUTCOME_LABELS,
    RETENTION_OUTCOME_LABEL_DICT,
    RETENTION_OUTCOME_CODE_DICT
)