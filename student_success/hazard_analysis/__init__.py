"""
Tools for performing and visualizing hazard analysis.

Submodules included:
- hazard_utils: Functions for filtering, assigning outcomes (graduated, not graduated, left major, ect), probability, and calculating K, r, and t1/2 from logistic data
- hazard_plots: Functions for plotting hazard ratio, cumulative probability, and curricular heatmaps

"""

from .hazard_utils import (
    prepare_and_process_data,
    process_student_data,
    assign_outcome_indicators,
    calculate_semester_interval,
    safe_eval,
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