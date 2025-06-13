"""
Utility functions for data wrangling and processing in student_success.

Included components:
--------------------
- io_utils :
    - Tools for file I/O, including column renaming from codebooks.
- scrambler :
    - Functions for anonymizing and restoring student IDs.
- program_utils :
    - Functions for metadata assignment, labeling, and lookup of information associated with majors and programs
- grade_utils :
     - functions for manipulation and cleaning of grade columns
- grades, time_utils, matriculation, etc. :
     - Additional support modules
"""
from dotenv import load_dotenv # included because users will need to have this installed to anonymize IDs

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
    lookup_major_name,
    replace_premajor_abbreviations
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
    RETENTION_OUTCOME_CODE_DICT,
    SANKEY_DISCIPLINE_GROUPS,
    SANKEY_DISCIPLINE_COLOR_MAP,
    DEMOGRAPHIC_COLOR_MAPS
)

from .time_utils import (
    adjust_grad_term,
    increment_semester,
    calculate_semester_interval,
    create_semesters,
    calculate_running_semester_number,
    combine_spring_summer_terms,
    get_academic_year,
    get_nth_year_fall_term,
    standardize_to_term_code
)