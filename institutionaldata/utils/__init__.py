"""
Utility functions for data wrangling and processing in institutionaldata.

Submodules included:
- io_utils: Tools for file I/O, including column renaming from codebooks.
- scrambler: Functions for anonymizing and restoring student IDs.
- program_utils: Functions for metadata assignment, labeling, and lookup of information associated with majors and programs
- grade_utils: functions for manipulation and cleaning of grade columns
- grades, time_utils, matriculation, etc.: Additional support modules.
"""

from .validation import validate_columns

from .demographics_utils import (
    set_up_demographic_flags,
    demographics_first_semester
)

from .grade_utils import (
    num_grade_normalized,
    num_grade_institutional,
    letter_grade_clean,
    letter_grade_simplify
)

from .io_utils import (
    load_grades,
    rename_columns_in_bulk,
    extract_column_mapping,
    flatten_column_mapping,
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
