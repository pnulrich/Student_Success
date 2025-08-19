"""
The `markov_diagrams` subpackage provides tools for building course progression
diagrams using Markov-style flows.

This package integrates preprocessing, flow analysis, and graph construction
to visualize how students progress through key course sequences.

Included components:
--------------------
- course_flows :
    Functions to calculate course-level statistics, including first/second attempt
    pass rates, repeat behavior, and alternate entry pathways.
- graph_builder :
    Utilities for constructing flow diagrams with `pydot`, embedding demographic
    pie charts, and rendering node/edge structures.
- preprocess :
    Data cleaning helpers to standardize course attempt data by limiting attempts
    and excluding unnecessary repeats.

Exposed functions:
------------------
- analyze_course :
    Compute detailed performance and progression statistics for a single course.
- calculate_progression_to_next_course :
    Estimate student progression probabilities into subsequent courses.
- calculate_alternate_entry :
    Quantify alternate entry into a course without the expected prerequisite.
- course_sequence_analysis :
    Build and render a complete course sequence diagram.

Notes
-----
- All functions assume course attempt data with columns:
  ``student_ID``, ``course_term``, ``course_grade_letter_simp``.
- Graph construction requires Graphviz and `pydot`.
- Demographic overlays are optional but supported when subgroup data is available.
"""

from .course_flows import analyze_course, calculate_progression_to_next_course, calculate_alternate_entry
from .graph_builder import course_sequence_analysis
