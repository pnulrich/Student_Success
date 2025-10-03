.. toctree::
   :hidden:
   :maxdepth: 1

Data Cleaning Walkthrough
-------------------------

Institutional datasets must be curated and pre-processed before analysis. This is an intensive
process that requires careful attention to details, variable naming conventions, and variation in
patterns that emerge in student data. This guide will familiarize you with common
cleaning steps and how to utilize resources in the student_success package.

Common Cleaning Tasks
=====================

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Task
     - Function / Logic
     - Notes
   * - Merge multiple CSV files
     - concatenate_csv_files
     - Reads and concatenates raw extracts into a single dataframe.
   * - Rename columns to package standards
     - rename_columns_in_bulk
     - Uses mapping spreadsheet to align institutional names with student_success conventions.
   * - Remove duplicate entries
     - pandas duplicated and .agg()
     - Eliminates redundant rows introduced by data queries
   * - De-identify student IDs
     - scramble_ID
     - Requires ``STUDENT_SUCCESS_CIPHER`` in .env for reproducibility.
   * - Merge spring and summer into a combined term
     - combine_spring_summer_terms
     - Ensures consistent academic year calculations and retention analysis.
   * - Calculate academic year from term code
     - get_academic_year
     - Converts institutional codes (YYYYMM) into academic year labels.
   * - Replace pre-major abbreviations
     - replace_premajor_abbreviations
     - Standardizes codes so students can be consistently classified.
   * - Add readable major names
     - lookup_major_name
     - Adds human-readable discipline names for reporting and visualization.
   * - Extract graduation dates
     - extract_bachelors_graduation_date
     - Identifies correct date when multiple graduations exist.
   * - Flag graduation in first major
     - classify_graduation_in_first_major
     - Returns 1 if student graduated in their initial major, else 0.
   * - Flag transfer students
     - custom flag_transfer logic
     - Checks if minimum term record shows ``transfer_credits > 0``.
   * - Identify students who took associates-level coursework first
     - associates_coursework_first flag
     - Compares earliest UA term with first bachelor’s term.
   * - Identify students who earned an associates before bachelor’s
     - associates_degree_first flag
     - Uses graduation date vs earliest bachelor’s term (with ±8-month tolerance).
   * - Filter out invalid rows
     - Conditional filtering
     - Drops students with inconsistent term ranges (e.g., UA terms after bachelor start).
   * - Restrict dataset to term range
     - Conditional filtering
     - Keeps only terms within study window and valid demographics values.




Load libraries
++++++++++++++
Start by loading utilities for data cleaning. These tools include the pandas package
and functions from various student_success modules for de-identification,
working with graduation dates, handling pre-major codes, creating new columns, and
standardizing column names.

The function load_rename_scramble consolidates repetitive steps: concatenating CSV files,
renaming columns, and de-identifying student IDs.

.. code-block:: python

    import pandas as pd
    import os
    from dotenv import load_dotenv
    import numpy as np
    import sys
    sys.path.append('../../../') # adjust as necessary so your student_success libraries can be reached
    import student_success.utils
    from student_success.utils.matriculation_utils import extract_bachelors_graduation_date
    from student_success.utils.time_utils import combine_spring_summer_terms, get_academic_year
    from student_success.utils.io_utils import concatenate_csv_files, rename_columns_in_bulk
    from student_success.utils.scrambler import scramble_ID
    from student_success.utils.program_utils import replace_premajor_abbreviations, lookup_major_name
    from student_success.metrics.flagging import classify_graduation_in_first_major

    load_dotenv()

    # Helper function to load multiple CSV files, rename columns for compatibility with the student_success
    # package, and de-identify students
    def load_rename_scramble(filename_list, column_mapping_file_path):
        df = concatenate_csv_files(filenames = filename_list)
        df = rename_columns_in_bulk(df = df, column_mapping_filepath = column_mapping_file_path)
        df = scramble_ID(input_data = df, cipher=os.environ['STUDENT_SUCCESS_CIPHER'])
        return df

Loading data and aggregating
+++++++++++++++++++++++++++++++++

Before working on a particular analysis, familiarize yourself with the variables needed in the subpackages
you would like to use (e.g., hazard analysis). Being familiar with the variables and data type required for
analysis should guide requests for data queries from your institutional research office. In this example, I will
be show code for wrangling a rough dataset into a usable format. I use the helper function load_rename_scramble()
to read the CSV and rename columns with standard naming conventions. column_mapping_file_path should point to
the codebook spreadsheet. You can enter your institution's column names there, and my functions will automatically
rename those to the ones used in student_success package.

.. code-block:: python

    filename_list = ["big_dataset.csv"]
    column_mapping_file_path = r'student_success\HHMI_IE3_codebook.xlsx'
    all_majors_full_df = load_rename_scramble(filename_list = filename_list, column_mapping_file_path = column_mapping_file_path)

At this stage, I have a single dataframe with standardized columns and scrambled IDs.

The dataset I was cleaning was comprised of a row for each student_ID for each
every semester and included information such as graduation dates, major at the given
semester, and demgoraphics. I also knew that my dataset included students who had
completed more than one degree program (associates, bachelors, double-majors, etc.) - these
had multiple rows for each term for every program. All data in those rows
was duplicated except for 'level_graduation', 'major_graduation', 'graduation_status', and
'graduation_date'. I aggregated these into tuples so that there would only be one row for
every 'course_term' / 'student_ID' combination. With large datasets, be aware that this
can be a time-intensive process. My CSV data source was ~70 MB. Aggregation required
~5 minutes.

.. code-block:: python

    aggregated_df = all_majors_full_df.groupby(['student_ID', 'course_term']).agg({
        'demographics_race': 'first',
        'demographics_sex': 'first',
        'term_college': 'first',
        'major_term': 'first',
        'concentration_term': 'first',
        'major2_term': 'first',
        'transfer_hours_term': 'first',
        'student_level': 'first',
        'term_level': 'first',
        'graduation_level': tuple,  # Coalescing into a tuple
        'major_graduation': tuple,  # Coalescing into a tuple
        'graduation_status': tuple,  # Coalescing into a tuple
        'graduation_date': tuple,  # Coalescing into a tuple
        'term_earliest_us': 'first',  # Keeping the first entry since the rows are fully duplicated
    }).reset_index()

Adding a column for academic year
+++++++++++++++++++++++++++++++++
An academic year column is helpful for filtering data in some functions. This can be added by get_academic_year(). I followed this up by forcing term columns to an
integer datatype.

.. code-block:: python

    aggregated_df['academic_year'] = aggregated_df['course_term'].apply(get_academic_year) # Determine the academic year of the term (added 2024-10-17 as modification to 2024-10-14 code)

    # enforce integer type for relevant columns
    for col in ['course_term', 'term_earliest_us', 'academic_year']:
        if not aggregated_df[col].isna().any():
            aggregated_df[col] = aggregated_df[col].astype('int32')

Limit to students with a full academic history
++++++++++++++++++++++++++++++++++++++++++++++
My dataset is from a query that includes all students for every semester. Because I plan to focus analysis on those students
as a function of how long they have been enrolled in university, I want to limit the dataset to students for whom I have their
entire academic history. Therefore, I filtered out all rows for which the earliest term of the bachelors degree was
not available. Additionally, I want to limit my dataset to  students whose first semester was Fall 2010
or later.

Using print statements provides feedback on the filtering process.

.. code-block:: python

    print(f'The original dataframe has {len(all_majors_full_df)} records and contains', all_majors_full_df['student_ID'].nunique(), 'unique student_ID')
    print(f'The aggregated dateframe is {len(aggregated_df)} records and contains', aggregated_df['student_ID'].nunique(), 'unique student_ID')

    # Exclude all students with NaN 'earliest_term_us'
    filtered_aggregated_df = aggregated_df[~aggregated_df['term_earliest_us'].isna()].copy()

    # Limit to students with 'earliest_term_us' of at least Fall 2010
    filtered_aggregated_df = filtered_aggregated_df[filtered_aggregated_df['term_earliest_us'] >= 201008]
    print(f'The filtered aggregated dateframe is {len(filtered_aggregated_df)} records and contains', filtered_aggregated_df['student_ID'].nunique(), 'unique student_ID')

Create a flag to identify students who took associates courses or earned an associates
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Recall that many students in my dataset took courses at the associates level ('student_level' == 'UA') before they began their
bachelor's degree. I flag these by adding two columns to the dataframe: 'associates_coursework_first' and
'associates_degree_first'.

In rare cases, a student takes associates level coursework after starting their bachelors.
I exclude these from my dataset because they represent rare situations and could inject unnecessary noise into analyses.

.. code-block:: python

    # Generate a list of student_ID who took associates-level courses before their bachelors
    students_with_associates_coursework_first = filtered_aggregated_df[(filtered_aggregated_df['course_term'] < filtered_aggregated_df['term_earliest_us']) &
        (filtered_aggregated_df['student_level'] == 'UA')]['student_ID'].unique()
    filtered_aggregated_df['associates_coursework_first'] = filtered_aggregated_df['student_ID'].isin(students_with_associates_coursework_first).astype(int)

    # Generate a list of student_ID who earned an associates before starting their bachelors program
    working_df = filtered_aggregated_df[filtered_aggregated_df['graduation_level'] == ('A',)][['student_ID', 'course_term', 'graduation_level', 'term_earliest_us','major_graduation', 'graduation_date']]
    working_df['graduation_date_first'] = working_df['graduation_date'].apply(lambda x: x[0] if len(x) > 0 else pd.NaT)
    working_df['graduation_date_first'] = pd.to_datetime(working_df['graduation_date_first'], errors='coerce')
    working_df['term_earliest_us'] = pd.to_datetime(working_df['term_earliest_us'], format='%Y%m', errors='coerce')
    working_df = working_df.dropna(subset=['term_earliest_us', 'graduation_date_first'])

    print("# students with an associates graduation at some point in the dataset:", working_df['student_ID'].nunique())
    print("# students who earned an associates degree before their first bachelor's level semester:", working_df[
        (working_df['graduation_level'].apply(lambda x: 'A' in x)) &
        (working_df['term_earliest_us'].dt.to_period('M') >= (working_df['graduation_date_first'].dt.to_period('M')-8))
        ]['student_ID'].nunique())

    associates_awarded_student_ids = working_df[
        (working_df['graduation_level'].apply(lambda x: 'A' in x)) &
        (working_df['term_earliest_us'].dt.to_period('M') >= working_df['graduation_date_first'].dt.to_period('M')-8)
        ]['student_ID']

    # create flag for students who have an associates awarded before the bachelors
    filtered_aggregated_df.loc[:, 'associates_degree_first'] = filtered_aggregated_df['student_ID'].isin(associates_awarded_student_ids).astype(int)

    print(f'filtered_aggregated_df has {len(filtered_aggregated_df)} records and contains', filtered_aggregated_df['student_ID'].nunique(), 'unique student_ID')
    print(f"filtered_aggregated_df has {len(filtered_aggregated_df[filtered_aggregated_df['associates_degree_first'] == 1])} records representing \
        {filtered_aggregated_df[filtered_aggregated_df['associates_degree_first'] == 1]['student_ID'].nunique()} unique student ID who completed associates degree at GSU first.")
    print(f"filtered_aggregated_df has {len(filtered_aggregated_df[filtered_aggregated_df['associates_degree_first'] == 0])} records representing \
        {filtered_aggregated_df[filtered_aggregated_df['associates_degree_first'] == 0]['student_ID'].nunique()} unique student ID who did not complete an associates at GSU first.")

    filtered_aggregated_df['associates_coursework_first'] = filtered_aggregated_df['student_ID'].isin(students_with_associates_coursework_first).astype(int)

    # Exclude all students who enrolled at associates level after starting a bachelor's level semester
    invalid_student_ids = filtered_aggregated_df[(filtered_aggregated_df['student_level'] == 'UA') &
        (filtered_aggregated_df['course_term'] >= filtered_aggregated_df['term_earliest_us'])]['student_ID'].unique()
    filtered_aggregated_df = filtered_aggregated_df[~filtered_aggregated_df['student_ID'].isin(invalid_student_ids)]

Renaming columns
++++++++++++++++
Functions in the student_success package rely on 'term_earliest' and 'demographics_term' so I rename columns 'term_earliest_us' and
'course_term'. I also ensure that 'term_earliest' has the correct datatype.

.. code-block:: python

    filtered_aggregated_df.rename(columns={'course_term': 'demographics_term'}, inplace=True)
    filtered_aggregated_df.rename(columns = {'term_earliest_us': 'term_earliest'}, inplace = True)
    filtered_aggregated_df['term_earliest'] = filtered_aggregated_df['term_earliest'].astype('int32')

Add a column for major associated with first term and a flag for transfer credit
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
I now create a columns to store each student's major declared the first term of their bachelors program and a column that
flags if a student started with transfer credit. Note that I like to work with a copy of my dataframe just in case I make
a mistake and need to revert to my backup copy without rerunning the prior steps.

.. code-block:: python

    merged_df['major_term_earliest'] = merged_df.apply(
        lambda row: row['major_term'] if row['demographics_term'] == row['term_earliest'] else None, axis=1
    )

    # Forward-fill the 'major_earliest_term' column to ensure the earliest major term is available across all rows for each student
    merged_df['major_term_earliest'] = merged_df.groupby('student_ID')['major_term_earliest'].ffill().bfill()

    # add  flag to indicate if a student had any transfer credits associated with their earliest demographics_term
    transfer_flags_df = merged_df.groupby('student_ID').apply(lambda x: 1 if (x.loc[x['demographics_term'] == x['demographics_term'].min(), 'transfer_hours_term'] > 0).any() else 0, include_groups=False).reset_index(name='flag_transfer')
    merged_df = merged_df.merge(transfer_flags_df, on='student_ID', how='left')

Want to combine Spring and Summer terms? There's a function for that!
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Summer terms present challenges to analyses of student progression. Should these be treated as equivalent to a Fall or Spring term?
Is comparison between a summer term and fall or spring term a fair comparison? If our analysis includes both students who
take courses in Fall, Spring, and Summer and students who take only Fall and Spring courses, how can we account for this?
What if we want to consider Summer as a lower credit "extension" of Spring for purposes of a study?

In anticipation of variations on experimental design, I generate both 'combined' and 'original' term types and report this
with new columns named 'term_type' and 'term_format'. This uses the function combine_spring_summer_terms(). In rare cases,
I have found that students graduate but later take courses as a post-baccalaureate. I am only interested in student progress
up to the graduation date so I drop rows for terms that occur after graduation with a bcahelors degree.

CAUTION: For large datasets, this is a computationally intensive step. With my datasets, this steps takes ~30 minutes.

.. code-block:: python

    merged_with_combined_terms_df = combine_spring_summer_terms(df = merged_df, remove_original = False)
    merged_with_combined_terms_with_BS_grad_date_df = extract_bachelors_graduation_date(merged_with_combined_terms_df)
    merged_with_combined_terms_with_BS_grad_date_cutoff_df = merged_with_combined_terms_with_BS_grad_date_df[
        (merged_with_combined_terms_with_BS_grad_date_df['graduation_date_bachelors'].isna()) |
        (pd.to_datetime(merged_with_combined_terms_with_BS_grad_date_df['demographics_term'].astype(int), format='%Y%m') <= merged_with_combined_terms_with_BS_grad_date_df['graduation_date_bachelors'])
    ]

A column flagging the row associated with a student's graduation term is very helpful but must be handled carefully
so both the 'combined' and 'original' term formats are appropriately labeled. I do this by filtering by term format into
two dataframes, flagging the graduation term for each dataframe, and concatenating into a full dataset.

.. code-block:: python

    # adding flags to merged_original_df
    max_course_term_df = merged_original_df.groupby('student_ID')['demographics_term'].max().reset_index()
    max_course_term_df.rename(columns={'demographics_term': 'max_course_term'}, inplace=True)

    merged_original_with_max_term_df = pd.merge(merged_original_df, max_course_term_df, on='student_ID')

    print(merged_original_df['student_ID'].nunique())
    print(merged_original_with_max_term_df['student_ID'].nunique())

    # Set `flag_graduation` using  max_course_term; 'flag_graduation' is an end_status overall
    merged_original_with_max_term_df['flag_graduation'] = (
        (merged_original_with_max_term_df['graduation_date_bachelors'].notna()) &
        (pd.to_datetime(merged_original_with_max_term_df['graduation_date_bachelors']) >=
         pd.to_datetime((merged_original_with_max_term_df['max_course_term'].astype(int)).astype(str), format='%Y%m'))
    ).astype(int)

    # Set `flag_graduation_term` using demographics_term == max_course_term; 'flag_graduation_term' identifies the term the student graduated
    # THIS GENERALLY WORKS BUT COULD BE PROBLEMATIC IF STUDENT's MAX_COURSE_TERM OCCURS AFTER GRADUATION
    merged_original_with_max_term_df['flag_graduation_term'] = (
        (merged_original_with_max_term_df['graduation_date_bachelors'].notna()) &
        (merged_original_with_max_term_df['demographics_term'] == merged_original_with_max_term_df['max_course_term'])).astype(int)

    # adding flags to the dataframe with semesters in combined format
    max_course_term_df = merged_combined_df.groupby('student_ID')['demographics_term'].max().reset_index()
    max_course_term_df.rename(columns={'demographics_term': 'max_course_term'}, inplace=True)

    merged_combined_with_max_term_df = pd.merge(merged_combined_df, max_course_term_df, on='student_ID')

    print(merged_combined_df['student_ID'].nunique())
    print(merged_combined_with_max_term_df['student_ID'].nunique())

    # Set `flag_graduation` using  max_course_term; 'flag_graduation' is an end_status overall
    merged_combined_with_max_term_df['flag_graduation'] = (
        (merged_combined_with_max_term_df['graduation_date_bachelors'].notna()) &
        (pd.to_datetime(merged_combined_with_max_term_df['graduation_date_bachelors']) >=
         pd.to_datetime((merged_combined_with_max_term_df['max_course_term'].astype(int)).astype(str), format='%Y%m'))
    ).astype(int)

    # Set `flag_graduation_term` using demographics_term == max_course_term; 'flag_graduation_term' identifies the term the student graduated
    # THIS GENERALLY WORKS BUT COULD BE PROBLEMATIC IF STUDENT's MAX_COURSE_TERM OCCURS AFTER GRADUATION
    merged_combined_with_max_term_df['flag_graduation_term'] = (
        (merged_combined_with_max_term_df['graduation_date_bachelors'].notna()) &
        (merged_combined_with_max_term_df['demographics_term'] == merged_combined_with_max_term_df['max_course_term'])).astype(int)

    # concatenate both dataframes into a single dataset
    full_df = pd.concat([merged_original_with_max_term_df, merged_combined_with_max_term_df[merged_combined_with_max_term_df['term_type'] != 'fall']], ignore_index=True)


Renaming columns for clarity
++++++++++++++++++++++++++++
Recall that students in my dataset could be from either bachelors level or associates level programs. I explicitly rename
several columns to avoid any confusion when I use the dataset later.

.. code-block:: python

    full_df.rename(columns = {
        'term_earliest': 'term_earliest_bachelors',
        'flag_graduation': 'flag_graduation_bachelors',
        'flag_graduation_term': 'flag_graduation_term_bachelors',
        'major_term_earliest': 'major_term_earliest_bachelors',
        'major_graduation': 'major_graduation_bachelors'
    }, inplace = True)

Flagging students who graduate in the same major they matriculated with
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
I create a column reporting whether a student graduated with the major associated with their first semester. Because
many programs have a pre-major code (e.g., nursing has an associated pre-major) and graduation major would not be equivalent to the
pre-major code, I use classify_graduation_in_first_major_bachelors() with the parameter pre_major_conversion = True.

NOTE: Graduation in major is relative to the major declared in the first BACHELORS semester on record.

For human readability, I also create a column 'major_term_name' that associates the full name of the major with abbreviations.

.. code-block:: python

    full_df['flag_graduation_in_first_major_bachelors'] = classify_graduation_in_first_major(df = full_df, major_col = 'major_graduation_bachelors', reference_col = 'major_term_earliest_bachelors', pre_major_conversion = True)
    full_df['major_term_name'] = full_df['major_term'].apply(lookup_major_name, pre_major_conversion = True)

Summary of columns and datatypes in the cleaned dataframe
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
After all of these cleaning steps, my final dataframe is comprised as follows:

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Column
     - Dtype
   * - student_ID
     - object
   * - demographics_term
     - int32
   * - demographics_race
     - object
   * - demographics_sex
     - object
   * - term_college
     - object
   * - major_term
     - object
   * - concentration_term
     - object
   * - major2_term
     - object
   * - transfer_hours_term
     - float64
   * - student_level
     - object
   * - term_level
     - object
   * - graduation_level
     - object
   * - major_graduation_bachelors
     - object
   * - graduation_status
     - object
   * - graduation_date
     - object
   * - term_earliest_bachelors
     - int32
   * - academic_year
     - int32
   * - associates_coursework_first
     - int32
   * - associates_degree_first
     - int32
   * - major_term_earliest_bachelors
     - object
   * - flag_transfer
     - int32
   * - year
     - int32
   * - term_code
     - int32
   * - term_type
     - object
   * - term_format
     - object
   * - graduation_date_bachelors
     - datetime64[ns]
   * - max_course_term
     - int32
   * - flag_graduation_bachelors
     - int32
   * - flag_graduation_term_bachelors
     - int32
   * - flag_graduation_in_first_major_bachelors
     - int32
   * - major_term_name
     - object

Saving as a CSV
+++++++++++++++
I save the final dataframe to a CSV for future use.

.. code-block:: python

    full_df.to_csv('clean_dataset.csv')
