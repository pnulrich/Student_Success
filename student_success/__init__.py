"""
Student Success Analysis Toolkit

The `student_success` package provides a modular framework for analyzing student
progression, retention, attrition, and academic outcomes. It includes tools for
hazard-based survival analysis, course-sequence visualization, metrics for
classifying outcomes, and general utilities for working with institutional data.

Subpackages
-----------
- hazard_analysis :
    Hazard models and visualization tools for analyzing persistence,
    attrition, graduation, and major-specific outcomes.

- markov_diagrams :
    Tools for constructing and visualizing Markov-style course flow diagrams,
    including demographic overlays and progression pathways.

- metrics :
    Functions for classifying student outcomes (e.g., graduation status,
    dropout term, retention in major) and supporting analyses.

- utils :
    General-purpose utilities for data cleaning, validation, time alignment,
    and ID scrambling.

Example
-------
A typical workflow might include:

>>> from student_success import hazard_analysis as hz
>>> df_prep, active_students = hz.hazard_utils.prepare_and_process_data(df, target_major="BIO")
>>> probs = hz.hazard_utils.calculate_probabilities(df_prep)
>>> hz.hazard_plots.plot_hazard_ratio(probs)

This package is designed for integration into institutional research pipelines
and reproducible analytics for student success initiatives.
"""


from . import hazard_analysis
from . import markov_diagrams
from . import metrics
from . import utils