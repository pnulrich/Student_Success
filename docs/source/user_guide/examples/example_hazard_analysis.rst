.. toctree::
   :hidden:
   :maxdepth: 1

Hazard Analysis Walkthrough
---------------------------
This example shows how to perform hazard analysis, generate instantaneous and
cumulative risk probabilities and plot heatmaps of course taking patterns.
Two data files are needed for this tutorial:
``examples/data/demonstration_datafile_hazard_coursework.csv``
``examples/data/demonstration_datafile_hazard_students.csv``

Loading Libraries and Sample Data
+++++++++++++++++++++++++++++++++

Import various packages and load the demo datafile into a pandas dataframe. Make sure your current working directory is
root directory of the student_success project.

.. code-block:: python

    import os
    import pandas as pd
    import importlib
    import sys
    from dotenv import load_dotenv
    sys.path.append('../../')

    from student_success.hazard_analysis import hazard_plots
    from student_success.hazard_analysis.hazard_utils import prepare_and_process_data, calculate_probabilities, extract_logistic_features
    from student_success.utils.time_utils import calculate_running_semester_number

    load_dotenv()


    # Load demonstration dataset
    coursework_path = "docs/examples/data/demonstration_datafile_hazard_coursework.csv"
    student_path = "docs/examples/data/demonstration_datafile_hazard_students.csv"
    example_coursework_df = pd.read_csv(coursework_path)
    example_student_df = pd.read_csm(student_path)


Take a look at the columns that are required for this type of analysis. The coursework dataframe
lists student coursework and grades by term. Student demographics, graduation info, and major
are provided for each semester in example_student_df.

.. code-block:: python

    print(example_coursework_df.columns)
    print(example_student_df.columns)


Data Processing
+++++++++++++++

Before analysis, we have to prepare the data, add various columns, and organize the data.
This is handled by prepare_and_process_data(). Filtering for features like academic year and
transfer credit upon their first semester can be handled by the function.The  major of interest and the course prefix
code for that major must be specified.

In the case below, the focus is on Biology majors and Biology courses for academic years 2012-2023 with essentially no
constraint on transfer credits.

.. code-block:: python

    academic_year_min = 2012
    academic_year_max = 2023
    transfer_credit_min = 0
    transfer_credit_max = 999
    target_major = 'BIO'
    target_major_course_prefix = "BIOL"
    inactivity_gap_threshold = 2

    # Call prepare_and_process_data to get outputs
    processed_df, target_major_courseload_df = prepare_and_process_data(
        student_major_data_df=example_student_df,
        coursework_df=example_coursework_df,
        target_major=target_major,
        transfer_credit_min = transfer_credit_min,
        transfer_credit_max=transfer_credit_max,
        target_major_course_prefix=target_major_course_prefix,
        academic_year_min = academic_year_min,
        academic_year_max = academic_year_max,
        inactivity_gap_threshold = 2
    )


Hazard probabilities are calculated prior to graphing. The function provides feedback on dataset size by printing
the number of students in full dataset and, if applicable, how many students in the dataset started in the fall term.

.. code-block:: python

    results = calculate_probabilities(processed_df)

Plotting Hazard Ratios
++++++++++++++++++++++

Use plot_hazard_ratio() to create a figure. Note that the file can be saved as a .png if save_file is set to True. You
can also specify if you want to plot only data for students whose time at college falls within a range of academic years.
min_academic_year and max_academic_year are solely used to generate the figure title.

The code below generates a multi-axis plot with line and scatter plots indicating the hazard ratio against the semester number.
This represents the probability that a student will experience a specific outcome at the end of that term. In this data set, for
example, the risk of changing majors (goldenrod) between semester 1 and 2 is 0.15. The secondary y-axis represents the
number of students in the starting cohort who are present at each semester. Semester 1 has the highest bar, and the bar
height becomes smaller as students leave the university or graduate.

.. code-block:: python

    hazard_plots.plot_hazard_ratio(
    proportions_df = results.get("proportions_df"),
    active_student_counts = results.get("active_student_counts"),
    target_major = 'BIO',
    min_academic_year = academic_year_min,
    max_academic_year = academic_year_max,
    max_semester_number = 11,
    # save_file = True,
    # file_name = 'example_hazard_plot'
    )


While plot_hazard_ratio() represents "instantaneous" probabilities of changing outcomes after a semester, plot_cumulative_probability()
allows us to illustrate the sum of the hazard ratios of an outcome across semesters. These plots typically have curves
characteristic of logistic or negative exponential functions. Again, the figure label is populated with manually-set
academic year ranges (the plotting function does not filter the data directly; this is solely for the figure label).

Note that an optional bar charts can be added on the secondary axis. The bar chart can either display the average number
of courses or credit hours taken in a semester for the target major.

.. code-block:: python

    hazard_plots.plot_cumulative_probability(
    cumulative_df = results["cumulative_df"],
    target_major_courseload_df = target_major_courseload_df,
    target_major = 'BIO',
    min_academic_year = academic_year_min,
    max_academic_year = academic_year_max,
    max_semester_number = 11,
    bar_chart_metric="avg_semester_courses_target_major",
    bar_chart_label=None,
    y_label="Cumulative Probability",
    # save_file = True,
    # file_name = 'example_cumulative_probability_number_courses'
    )

.. image:: /_static/figures/example_cumulative_probability_number_courses.png
   :alt: example of cumulative probability of outcomes in BIO majors with average semester courses as secondary bar chart
   :align: center
   :width: 600px

.. code-block:: python

    hazard_plots.plot_cumulative_probability(
    cumulative_df = results["cumulative_df"],
    target_major_courseload_df = target_major_courseload_df,
    target_major = 'BIO',
    min_academic_year = academic_year_min,
    max_academic_year = academic_year_max,
    max_semester_number = 11,
    bar_chart_metric="avg_semester_credits_target_major",
    bar_chart_label=None,
    y_label="Cumulative Probability",
    # save_file = True,
    # file_name = 'example_cumulative_probability_number_credits')

.. image:: /_static/figures/example_cumulative_probability_number_credits.png
   :alt: example of cumulative probability of outcomes in BIO majors with average credit hours as secondary bar chart
   :align: center
   :width: 600px

Fitting a Logistic Equation to Outcomes
+++++++++++++++++++++++++++++++++++++++

Let's imagine that you would like to use a logistic equation to each of the outcome curves. You can do this with
extract_logistic_features(). Outcomes are coded as as an integer from 1-4 where

        - -1 : No change from prior term; student continues in same major.
        -  1 : Left the university after this term (inactivity for 2+ terms, no graduation).
        -  2 : Graduated in their original declared major in this term.
        -  3 : Graduated in a different major in this term.
        -  4 : Actively changed major in this term (compared to previous term).

.. code-block:: python

    for i in [1,2,3,4]:
        print(extract_logistic_features(i, results['cumulative_df']['semester_number'], results['cumulative_df'][i]))

The output of this command is:
    {'Outcome': 1, 'K': 0.3709652852908718, 'r': 0.6541227655326407, 't_half': 3.271569391269526}

    {'Outcome': 2, 'K': 0.2774413248930473, 'r': 0.6975405206264437, 't_half': 8.944415101561583}

    {'Outcome': 3, 'K': 0.27370157350615926, 'r': 0.6257332334199042, 't_half': 9.707007943940953}

    {'Outcome': 4, 'K': 0.39867929429617194, 'r': 0.36204067345191815, 't_half': 1.396193156854709}

Identifying Timing of Classes that Students are Taking
++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are interested *when* students take specific courses, utilize plot_course_heatmap(). This uses the bokeh framework
to generate an interactive map of patterns in course timing. The most common courses students enroll in are shown in the rows,
with the color representing the portion of students in the target major that take that course in semester X. Cooler color
indicates lower proportion, and warmer colors indicate a higher proportion. If you hover over a cell, a tool tip will
tell you how many students are in that group and what proportion they represent of active students in the target major at that
semester.

.. code-block:: python

    academic_year_min = 2012
    academic_year_max = 2023
    transfer_credit_min = 0
    transfer_credit_max = 999  # Adjust as needed
    target_major = 'BIO'
    target_major_course_prefix = "BIOL"

    hazard_plots.plot_course_heatmap(
        filtered_df = processed_df,
        target_major = target_major,
        transfer_credit_min = transfer_credit_min,
        transfer_credit_max = transfer_credit_max,
        min_academic_year= academic_year_min,
        max_academic_year= academic_year_max,
        minimum_student_number= 50,
        # save_file= True,
        # file_name= 'example_course_heatmap.html'
    )

.. only:: html

    .. raw:: html

        <iframe src = "../../_static/figures/example_course_heatmap.html"
            width = "100%" height="500" style = "border:none;"></iframe>

Visualizing Outcomes and Changes in Major Status with Sankey Plots
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Flow of students among outcome codes is illustrated with Sankey plots. Distribution of active students in each outcome
pool is indicated by the size of the bar for each semester. Proportions of these "flow" to outcomes shown in the bars on
the right side of the graph. The graphs are interactive and provide hover-tips providing information on the number of students
in a bar or flow. Bars can be dragged to new locations to help with viewing specific features of the plot.

.. code-block:: python

    create_sankey_plot(
    data = example_student_df[(
        (example_student_df['major_term_earliest'] == 'BIO') &
        (example_student_df['semester_number'] <=12) &
        (example_student_df['term_earliest'] <= 201805)
    )].copy(),
    target_major = 'BIO',
    plot_title = '',
    target_major_name = 'Biology')

.. only:: html

    .. raw:: html

        <iframe src = "../../_static/figures/example_sankey.html"
            width = "100%" height ="700" style = "border:none;"></iframe>