"""
Hazard analysis tools for modeling student progression, attrition, and major-specific outcomes.

The `hazard_analysis` subpackage provides a framework for analyzing academic persistence using hazard-based methods.
It includes tools for calculating cumulative probabilities, estimating logistic survival parameters (K, r, t1/2),
and visualizing dropout, graduation, and course progression dynamics.

Included components:
--------------------
- `hazard_utils`:
    - Filters and prepares data for analysis
    - Assigns outcome indicators (e.g., graduation, major switching, dropout)
    - Calculates cumulative probabilities and fits logistic curves

- `hazard_plots`:
    - Visualizes hazard ratios and cumulative probabilities across terms
    - Generates heatmaps of course enrollment patterns among active students

- `sankey`:
    - Constructs Sankey diagrams illustrating student pathways from matriculation through completion or departure

Utility integrations:
---------------------
- Functions from `student_success.metrics.flagging` support classification of graduation and dropout behavior
- Validation and time utilities ensure proper formatting, column validation, and semester alignment

Example Use:
------------
This module supports full hazard pipelines such as:

- Preparing and processing a student-major dataset for a given target major (e.g., "BIO")
- Computing progression metrics across semesters
- Visualizing patterns of course enrollment or attrition using heatmaps and Sankey plots
"""


from .hazard_utils import (
    prepare_and_process_data,
    assign_outcome_indicators,
    calculate_semester_interval,
    calculate_probabilities,
    extract_logistic_features,

)

from student_success.metrics.flagging import (
    classify_dropout_term,
    classify_graduation_term,
    classify_graduation_in_major,
    classify_graduation_in_STEM,
    classify_graduation_status
)

from student_success.utils.validation import (
    safe_parse_tuple,
    validate_columns
)

from student_success.utils.time_utils import (calculate_semester_interval)

from .hazard_plots import (
    plot_hazard_ratio,
    plot_cumulative_probability,
    plot_course_heatmap,
    prepare_course_heatmap_data,
)

from .sankey import (
    create_sankey_plot
)