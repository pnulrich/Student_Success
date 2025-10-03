Workflows
=========

The ``student_success`` package provides end-to-end analytics workflows for student progression, retention, and course performance. Each workflow combines utilities, metrics, and visualization tools. Below are key capabilities and example outputs.

Data Cleaning
-------------
Cleans and normalizes raw institutional data into analyzable structures. Common tasks include:
- Standardizing term codes
- Flagging transfer students and associate coursework
- Filtering invalid records and ranges
- Producing tidy tables for downstream analysis

Example: see :doc:`examples/data_cleaning` for a complete walkthrough.

Hazard Analysis
---------------
Models student retention and attrition across semesters. Capabilities:
- Assigning retention outcomes (retained, leaver, graduated)
- Calculating cumulative probabilities and hazard ratios
- Visualizing retention curves over time

Outputs from these resources provide time-based insight into student behavior since matriculation. A visualization of a
hazard analysis is shown below for a hypothetical cohort of biology majors.

.. figure:: ../_static/figures/example_hazard_plot.png
   :alt: Example hazard analysis plot
   :width: 70%

Interactive visualizations of flows between majors and patterns in which courses are taken are also available. Below is an
interactive heat map that illustrating when members of a student cohort take various courses during their degree program.

.. only:: html

    .. raw:: html

        <iframe src = "../_static/figures/example_course_heatmap.html"
            width = "100%" height="500" style = "border:none;"></iframe>

See :doc:`examples/example_hazard_analysis` for details.

Markov Diagrams
---------------
Visualizes flows of students between majors or statuses. Features:
- Transition probabilities between states
- Sankey/Markov diagrams with node styling
- Options for demographic overlays (e.g., sex, PELL status)

Outputs from these resources can produce single or multiple course flows with customizable pie charts. An example of a
single-course Markov diagram is shown below.

.. figure:: ../_static/figures/example_markov_one_course.png
   :alt: single-course, markov flow example
   :align: center
   :width: 450px

See :doc:`examples/example_markov_diagrams` for details.
