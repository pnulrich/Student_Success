"""
The `metrics` subpackage provides classification tools for retention and graduation analysis.

This package contains functions for assigning retention outcomes, classifying dropout
and graduation terms, and evaluating student completion patterns in relation to major
and STEM affiliation. These functions are designed to support student success analytics
at the term and program level.
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