Creating Markov Diagrams
------------------------
This example shows how to generate a two–course Markov diagram using a fake dataset included with the documentation.
The data file is located at ``examples/data/demonstration_datafile_markov.csv``

Walkthrough
^^^^^^^^^^^

Import various packages and load the demo datafile into a pandas dataframe. Make sure your current working directory is
root directory of the student_success project.

.. code-block:: python

   import pandas as pd
   from student_success.utils import grade_utils, filter_valid_letter_grades, set_up_demographic_flags
   from student_success.markov_diagrams.preprocess import prepare_course_attempts
   from student_success.markov_diagrams.graph_builder import course_sequence_analysis

   # Load demonstration dataset
   demo_path = "docs/examples/data/demonstration_datafile_markov.csv"
   demo_df = pd.read_csv(demo_path)

The datafile contains several different classes, but we are only interested in the introductory chemistry sequence. In our dataset,
these course numbers are CHEM1211 and CHEM1212. Filter demo_df to create a dataframe for each course.

.. code-block:: python

   # ----------------------------------------------------------------------
   # Prepare Chemistry 1 and Chemistry 2 subsets for analysis
   # ----------------------------------------------------------------------
   chem1_df = demo_df[(
       (demo_df["course_prefix"] == "CHEM") &
       (demo_df["course_number"] == 1211)
   )].copy()

   chem2_df = demo_df[(
       (demo_df["course_prefix"] == "CHEM") &
       (demo_df["course_number"] == 1212)
   )].copy()

   # graphing functions expect the term column to be named 'course_term'
   chem1_df = chem1_df.rename({'demographics_term': 'course_term'}, axis=1)
   chem2_df = chem2_df.rename({'demographics_term': 'course_term'}, axis=1)
Some pre-processing should be performed prior to creating the diagram. By giving descriptive titles to the courses, our diagrams will be labeled well.
The example dataset uses +/- grading scales so we use the letter_grade_simplify() utility to strip these.


.. code-block:: python

   # Set a descriptive course title
   chem1_df["course_title"] = "Introductory Chemistry I"
   chem2_df["course_title"] = "Introductory Chemistry II"

    # Simplify letter grades by eliminating + or - designations. If your institution considers a C- as a non-passing grade, c_minus_flag should be set to 1.
   chem1_df = grade_utils.letter_grade_simplify(dataframe=chem1_df, c_minus_flag=0)
   chem2_df = grade_utils.letter_grade_simplify(dataframe=chem2_df, c_minus_flag=0)



Since the large majority of students attempt these course no more than two times, we will limit our graph to the first and second attempts.
We only want to consider letter grades (including W) as valid so we use the valid_grade_parameter to ensure that other categories
(like incomplete or audit codes) are not included.

.. code-block:: python

   # ----------------------------------------------------------------------
   # Consider only the first/second attempts and filter out invalid grades
   # ----------------------------------------------------------------------
   chem1_attempts_df = prepare_course_attempts(chem1_df)
   chem2_attempts_df = prepare_course_attempts(chem2_df)

   chem1_attempts_df = filter_valid_letter_grades(
       df=chem1_attempts_df,
       grade_col="course_grade_letter_simp",
       valid_grades=["A", "B", "C", "D", "F", "W"]
   )
   chem2_attempts_df = filter_valid_letter_grades(
       df=chem2_attempts_df,
       grade_col="course_grade_letter_simp",
       valid_grades=["A", "B", "C", "D", "F", "W"]
   )

   # Concatenate the dataframes
   chem1_chem2_attempts_df = pd.concat(
       [chem1_attempts_df, chem2_attempts_df],
       ignore_index=True
   )

The markov_diagrams subpackage can plot demographic proportions alongside key nodes. Our dataframe conveniently has columns with
called 'demographic_sex' and 'demographics_race'. The values need to be recoded in a numeric format to create the plot.
We will use set_up_demographic_flags() from utils.demographics_utils to do this.

.. code-block:: python

   chem1_chem2_attempts_df = set_up_demographic_flags(df = chem1_chem2_attempts_df, peer = True, sex = True)

We're read to build our Markov diagram! We will focus on chemistry majors, and our final graph will display the sex proportions
at key nodes. (Don't want pie charts included? Set node_pie to False.) You can export your figures to png as desired.

First, let's limit the graph to biology majors taking the first course in the chemistry sequence. The connections between
nodes are called edges. Edge labels indicate proportion of students moving through the path, and absolute numbers are
given in parenthesis. In this graph, note that 14% of students had grades of DFW in their first attempt. This represents 41
of the original 292 students in the course. The pie charts represent the proportion of females (green) and males (blue)
in nodes. Pie chart colors can be customized in ``utils.constants.DEMOGRAPHIC_COLOR_MAPS``.

.. code-block:: python

    target_major = "BIO"

    sequence = [
        "Introductory Chemistry I"
    ]

    graph = course_sequence_analysis(
        course_sequence=sequence,
        df=chem1_chem2_attempts_df,
        major_matriculation_column="major_term_earliest",
        target_major_code=target_major,
        node_pie=True,
        demographics_flag_col="flag_sex",
    )


.. image:: /_static/figures/example_markov_one_course.png
   :alt: single course, markov diagram example
   :align: center
   :width: 600px

You can expand to two or more courses by adding subsequent courses to the sequence list. The order in the sequence
is important and should be listed  in order they must be taken by students.

.. code-block:: python

   target_major = "CHM"

   sequence = [
      "Introductory Chemistry I",
      "Introductory Chemistry II",
   ]

   graph = course_sequence_analysis(
     course_sequence=sequence,
     df=chem1_chem2_attempts_df,
     major_matriculation_column="major_term_earliest",
     target_major_code=target_major,
     node_pie=True,
     demographics_flag_col="flag_sex",
   )

.. image:: /_static/figures/example_markov_two_courses.png
   :alt: multi-course, markov example
   :align: center
   :width: 600px
