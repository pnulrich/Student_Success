"""
Hazard analysis tools for modeling student persistence, graduation, and attrition.

The `hazard_analysis` subpackage provides methods for studying academic progression
using hazard-based approaches. It supports filtering and preparing student data,
calculating cumulative probabilities of events (graduation, dropout, major change),
fitting logistic survival curves, and visualizing outcomes.

Included components:
--------------------
- `hazard_utils`:
    - Prepare and filter student datasets
    - Assign outcome indicators (graduation, dropout, major switching)
    - Compute cumulative probabilities and fit logistic curves

- `hazard_plots`:
    - Plot hazard ratios and cumulative probabilities by semester
    - Generate heatmaps of course enrollment among active students

- `sankey`:
    - Build Sankey diagrams to visualize flows from matriculation
      through graduation, switching majors, or leaving college

Utility integrations:
---------------------
- Relies on `student_success.metrics.flagging` for classifying outcomes
- Uses validation and time utilities for column checks and semester alignment

Example Use:
------------
A typical hazard pipeline involves:
1. Preparing and processing a student-major dataset (e.g., for "BIO")
2. Calculating probabilities of persistence, graduation, or attrition across terms
3. Visualizing results with hazard plots, heatmaps, or Sankey diagrams

See Also:
---------
- `student_success.markov_diagrams` :
    Tools for modeling course progression and student flows
    using Markov chain–based methods.
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
