"""
utils
=====

General-purpose utility functions and constants for data wrangling, cleaning,
and processing in the ``student_success`` package. The subpackage consolidates
common tools used across analysis modules, ensuring consistency in
preprocessing and interpretation of student success data.

Included components
-------------------
- io_utils
    File I/O helpers, including functions for bulk CSV concatenation,
    column renaming via codebooks, and flattening of column mapping structures.
- scrambler
    ID anonymization and de-anonymization utilities using a cipher.
- program_utils
    Functions for classifying and labeling majors and programs,
    including discipline groupings and premajor-to-major mappings.
- grade_utils
    Functions for cleaning, normalizing, and simplifying letter and
    numeric grades, plus filters for valid grade subsets.
- demographics_utils
    Utilities for setting demographic flags and identifying first-semester
    enrollment based on demographic records.
- matriculation_utils
    Functions for cleaning and validating matriculation terms and
    adjusting institutional entry records.
- time_utils
    Tools for working with academic term codes and semester intervals,
    including calendar standardization, sequence generation, and
    combined spring/summer terms.
- validation
    Lightweight utilities for validating DataFrame schema and safely parsing
    tuple-like values from messy inputs.
- constants
    Shared dictionaries and lookup tables for majors, disciplines, retention
    outcomes, Sankey visualizations, demographic colors, GPA mappings,
    and semester code definitions.

Notes
-----
These modules are designed to be general-purpose within the package and
serve as foundational building blocks for higher-level analysis in metrics,
hazard analysis, and visualization subpackages.
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
    DEMOGRAPHIC_COLOR_MAPS,
    LETTER_GRADE_GPA_MAP,
    GRADE_SIMPLIFICATION_MAP,
    SEMESTER_NUMERIC_CODES
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
