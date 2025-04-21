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

from .hazard_plots import (
    plot_hazard_ratio,
    plot_cumulative_probability,
    plot_course_heatmap,
    prepare_course_heatmap_data,
)
