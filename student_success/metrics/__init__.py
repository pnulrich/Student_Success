"""
metrics
=======

The ``metrics`` subpackage provides classification utilities for student
retention and graduation analysis. These functions assign categorical
outcomes that describe whether students persist, graduate, or drop out,
and whether graduation occurs in their first major or within STEM.

Core capabilities include:
---------------------------
- Retention outcomes:
    Assigns categorical indicators for persistence, attrition, or
    graduation, suitable for survival, hazard, and Sankey analysis.
- Dropout classification:
    Identifies the academic term in which a student is considered to
    have dropped out based on enrollment gaps or inactivity.
- Graduation classification:
    Flags graduation terms and statuses, distinguishing between:
      • Overall graduation
      • Graduation in a student's original major
      • Graduation in STEM fields

Notes
-----
- These functions rely on standardized term codes (YYYYTT) and the
  discipline/major mappings defined in ``utils.constants``.
- Output is intended to integrate with visualization and modeling tools
  in ``hazard_analysis`` and ``markov_diagrams``.
"""


from .flagging import (
    assign_retention_outcomes,
    classify_dropout_term,
    classify_graduation_term,
    classify_graduation_status,
    classify_graduation_in_major,
    classify_graduation_in_first_major,
    classify_graduation_in_STEM
)