import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, ColorBar
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256


def plot_hazard_ratio(
        proportions_df,
        active_student_counts,
        target_major,
        min_academic_year,
        max_academic_year,
        max_semester_number=None
):
    """
    Plot hazard ratios for student outcomes by semester (lines) with active student counts (bars).

    Parameters
    ----------
    proportions_df : pandas.DataFrame
        A DataFrame containing proportions for each outcome by semester.
        Columns should include:
        - 'semester_number': Semester identifier.
        - Outcome columns (e.g., 1 for Left College, 2 for Graduated in Target Major).

    active_student_counts : pandas.Series
        A Series with the total number of active students per semester.

    target_major : str
        The name of the target major being analyzed (e.g., 'BIO').

    min_academic_year : int
        The earliest academic year in the cohort.

    max_academic_year : int
        The latest academic year in the cohort.

    max_semester_number : int, optional
        The maximum semester to display on the x-axis. If None, uses data max.

    Returns
    -------
    None
        Displays the hazard ratio plot.
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar plot for total students
    ax1.bar(
        proportions_df["semester_number"],
        active_student_counts,
        alpha=0.2, color="gray", edgecolor="black"
    )
    ax1.set_ylabel("# of Active Students (any major)", fontsize=16, color='black', rotation=270, labelpad=20)
    ax1.set_xlabel("Semester Number", fontsize=16, color='black')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=12, length=10)
    ax1.tick_params(axis='x', labelcolor='black', labelsize=12, length=10)

    # Line plot for hazard ratios
    ax2 = ax1.twinx()
    labels_colors = {
        1: ("Left College", "red"),
        2: (f"Graduated, {target_major}", "green"),
        3: ("Graduated, Other", "blue"),
        4: ("Changed Major", "goldenrod")
    }
    markers = {1: 'x', 2: '+', 3: 'o', 4: '.'}

    for code, (label, color) in labels_colors.items():
        if code in proportions_df.columns:
            ax2.plot(
                proportions_df["semester_number"],
                proportions_df[code],
                marker=markers[code], linestyle='-', label=label, color=color
            )

    ax2.set_ylabel("Hazard Ratio", fontsize=16, color='purple')
    ax2.tick_params(axis='y', labelcolor='purple', labelsize=12, length=10)
    ax2.set_ylim(0, 0.3)

    # Relocate axes to opposite sides of the graph
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position("right")
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")

    # Title and x-axis limits
    fig.suptitle(
        f"Outcomes by Semester ({target_major}, Fall Cohorts: AY{min_academic_year}-{max_academic_year})",
        fontsize=14
    )
    if max_semester_number:
        ax2.set_xlim(0.5, max_semester_number + 0.5)
    else:
        ax2.set_xlim(0.5, proportions_df["semester_number"].max() + 0.5)

    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.show()


def prepare_course_heatmap_data(filtered_df, target_major, min_academic_year, max_academic_year, number_top_courses=5,
                                minimum_student_number=10, minimum_proportion_active_students=0.02):
    """
    Prepare course frequency and proportion data for heatmap visualization.

    This function filters student-course data to focus on active students within a target major
    and academic year range. It computes the proportion of students taking each course per semester,
    and retains only the top courses by prevalence, subject to minimum thresholds.

    Parameters
    ----------
    filtered_df : pandas.DataFrame
        DataFrame containing filtered student records. Required columns:
        - 'academic_year'
        - 'major_term'
        - 'course_list'
        - 'semester_number'
        - 'student_ID'
    target_major : str
        Target major to restrict analysis to (e.g., 'BIO').
    min_academic_year : int
        Minimum academic year to include (inclusive).
    max_academic_year : int
        Maximum academic year to include (inclusive).
    number_top_courses : int, optional
        Number of top courses to retain per semester (default is 5).
    minimum_student_number : int, optional
        Minimum number of active students in a semester for a course to be considered (default is 10).
    minimum_proportion_active_students : float, optional
        Minimum proportion of active students taking a course in a semester (default is 0.02).

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns:
        - 'course_list': Course identifiers (e.g., 'BIOL2107')
        - 'semester_number': Semester index.
        - 'proportion': Proportion of active students enrolled in the course.
        - 'frequency': Number of students enrolled in the course.

    Notes
    -----
    - Courses are retained only if they meet both the proportion and student count thresholds.
    - The top `number_top_courses` are selected per semester based on enrollment proportion.
    - Designed to support Bokeh or matplotlib-based heatmap plotting.
    """

    if number_top_courses <= 0:
        raise ValueError("number_top_courses must be greater than 0")
    if not (0 <= minimum_proportion_active_students <= 1):
        raise ValueError("minimum_proportion_active_students must be between 0 and 1")
    if minimum_student_number <= 0:
        raise ValueError("minimum_student_number must be greater than 0")

    df = filtered_df.copy()

    # Apply academic year filtering
    df = df[(df['academic_year'] >= min_academic_year) & (df['academic_year'] <= max_academic_year)]

    # Focus on retained majors only
    df = df[df['major_term'] == target_major]

    # Ensure course_list is a list
    df['course_list'] = df['course_list'].fillna("").apply(lambda x: x if isinstance(x, list) else [])

    # Explode the course list into individual rows for frequency calculation
    exploded_courses = df.explode('course_list')
    course_frequencies = (
        exploded_courses.groupby(['semester_number', 'course_list'])['student_ID']
        .nunique()
        .reset_index(name='frequency')
    )

    # Active student counts per semester
    active_counts = df.groupby('semester_number')['student_ID'].nunique().reset_index(name='active_student_count')

    # Merge and calculate proportions
    data = course_frequencies.merge(active_counts, on='semester_number', how='left')
    data['active_student_proportion'] = data['frequency'] / data['active_student_count']

    # Filter and select top courses
    top_courses = (
        data[
            (data['active_student_proportion'] > minimum_proportion_active_students) &
            (data['active_student_count'] >= minimum_student_number)
            ]
        .groupby('semester_number')
        .apply(lambda x: x.nlargest(number_top_courses, 'active_student_proportion').assign(semester_number=x.name))
        .reset_index(drop=True)
    )

    # Final reshape
    return top_courses[['course_list', 'semester_number', 'active_student_proportion', 'frequency']].rename(
        columns={'active_student_proportion': 'proportion'}
    )


def plot_course_heatmap(
        filtered_df,
        target_major,
        transfer_credit_min,
        transfer_credit_max,
        min_academic_year,
        max_academic_year,
        number_top_courses=5,
        minimum_student_number=100,
        minimum_proportion_active_students=0.02,
):
    """
    Plot a heatmap of the proportion of active students enrolled in top courses over time.

    Parameters
    ----------
    filtered_df : pandas.DataFrame
        A DataFrame containing student and course data.
    target_major : str
        The target major being analyzed (e.g., 'BIO').
    transfer_credit_min : int
        Minimum transfer credits required for inclusion in the analysis.
    transfer_credit_max : int
        Maximum transfer credits allowed for inclusion in the analysis.
    min_academic_year : int
        The earliest academic year in the cohort.
    max_academic_year : int
        The latest academic year in the cohort.
    number_top_courses : int, optional
        The number of top courses with the highest proportions to include in the heatmap. Default is 5.
    minimum_student_number : int, optional
        Minimum number of students for a course to be included. Default is 100.
    minimum_proportion_active_students : float, optional
        Minimum proportion of active students in a course to be included. Default is 0.02.

    Returns
    -------
    None. Displays an interactive Bokeh heatmap of course enrollment proportions.

    Notes
    -------
    - This function is a visualization wrapper for `prepare_course_heatmap_data`.
    - The heatmap reflects students in the `target_major` who remain active each semester.
    """

    heatmap_df = prepare_course_heatmap_data(
        filtered_df=filtered_df,
        target_major=target_major,
        min_academic_year=min_academic_year,
        max_academic_year=max_academic_year,
        number_top_courses=number_top_courses,
        minimum_student_number=minimum_student_number,
        minimum_proportion_active_students=minimum_proportion_active_students,
    )

    # Prepare plot axes
    heatmap_df['semester_number'] = heatmap_df['semester_number'].astype(str)
    heatmap_df['course_list'] = heatmap_df['course_list'].astype(str)
    x_range = list(map(str, sorted(heatmap_df['semester_number'].astype(int).unique())))
    y_range = sorted(heatmap_df['course_list'].unique())

    # Define color mapper
    color_mapper = linear_cmap(
        field_name='proportion', palette=Viridis256,
        low=heatmap_df['proportion'].min(),
        high=heatmap_df['proportion'].max()
    )

    # Create Bokeh figure
    p = figure(
        title=f"Proportion Active {target_major} Majors in Top {number_top_courses} Courses ({target_major}, Fall Cohorts: AY{min_academic_year}-{max_academic_year}, Transfer Credits: {transfer_credit_min}-{transfer_credit_max})",
        x_axis_label="Semester Number",
        y_axis_label="Course Number",
        x_range=x_range,
        y_range=y_range,
        width=800, height=400,
        tools="hover", tooltips=[("Proportion", "@proportion{0.00}"), ("# of students", "@frequency{0}")]
    )

    source = ColumnDataSource(heatmap_df)
    p.rect(
        x="semester_number", y="course_list", width=1, height=1,
        source=source, line_color=None, fill_color=color_mapper
    )

    color_bar = ColorBar(color_mapper=color_mapper['transform'], width=8, location=(0, 0))
    p.add_layout(color_bar, 'right')

    show(p)


def plot_cumulative_probability(
        cumulative_df,
        target_major,
        min_academic_year,
        max_academic_year,
        target_major_courseload_df,
        max_semester_number,
        bar_chart_metric="avg_semester_courses_target_major",
        bar_chart_label=None,
        y_label="Cumulative Probability"
):
    """
    Plot cumulative probabilities of student outcomes by semester with an accompanying bar chart.
    This function visualizes cumulative probabilities of outcomes (e.g., leaving, graduating)
    as lines, with an optional bar chart representing a metric such as average courses or credits.

    Parameters
    ----------
    cumulative_df : pandas.DataFrame
        DataFrame containing cumulative outcome probabilities by semester.
        Must include 'semester_number' and outcome columns (e.g., 1, 2, 3, 4).

    target_major : str
        Target major being analyzed (e.g., 'BIO').

    min_academic_year : int
        Earliest academic year in the cohort.

    max_academic_year : int
        Latest academic year in the cohort.

    target_major_courseload_df : pandas.DataFrame
        DataFrame with average course load or credit info per semester.
        Must include 'semester_number' and bar_chart_metric.

    max_semester_number : int
        Max semester to display on the x-axis.

    bar_chart_metric : str, optional
        Column name in `target_major_courseload_df` to use as bar height per semester (default is "avg_semester_courses_target_major").
        Metric options from hazard_utils.prepare_and_process_data() also include avg_semester_credits_target_major

    bar_chart_label : str, optional
        Y-axis label for bar chart. If None, it will be auto-generated from metric.

    y_label : str, optional
        Y-axis label for the cumulative probability plot (default is "Cumulative Probability").

    Returns
    -------
    None
        Displays the plot using matplotlib.

    Notes
    -----
    - This plot overlays average semester metrics (courses or credits) with cumulative student outcomes.
    - Use `hazard_utils.prepare_and_process_data()` to precompute the input dataframes.
    """

    # Auto-generate bar chart label if not provided
    if bar_chart_label is None:
        if "courses" in bar_chart_metric:
            bar_chart_label = f"Mean # {target_major} courses"
        elif "credits" in bar_chart_metric:
            bar_chart_label = f"Mean {target_major} credit hours"
        else:
            bar_chart_label = bar_chart_metric

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart: average course load (or other metric) on the primary y-axis
    ax1.bar(
        target_major_courseload_df['semester_number'],
        target_major_courseload_df[bar_chart_metric],
        facecolor=(0, 0, 1, 0.15),
        edgecolor=(0, 0, 0, 1)
    )
    ax1.set_ylabel(bar_chart_label, fontsize=16, rotation=270, color='black', labelpad=20)
    ax1.set_xlabel("Semester Number", fontsize=16, color='black')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=12)
    ax1.tick_params(axis='x', labelcolor='black', labelsize=12)

    # Line chart: cumulative outcome probabilities on the secondary y-axis
    ax2 = ax1.twinx()
    labels_colors = {
        1: ("Left College", "red"),
        2: (f"Graduated, {target_major}", "green"),
        3: ("Graduated, Other", "blue"),
        4: ("Changed Major", "goldenrod")
    }
    markers = {1: 'x', 2: '+', 3: 'o', 4: '.'}

    for code, (label, color) in labels_colors.items():
        if code in cumulative_df.columns:
            ax2.plot(
                cumulative_df["semester_number"],
                cumulative_df[code],
                marker=markers[code],
                linestyle='-',
                label=label,
                color=color
            )

    ax2.set_ylabel(y_label, fontsize=16, color='black', labelpad=10)
    ax2.tick_params(axis='y', labelcolor='black', labelsize=12)
    ax2.set_ylim(0, 0.5)

    # Flip sides
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position("right")
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")

    # Title and x-axis range
    fig.suptitle(
        f"Cumulative Outcome Probability ({target_major}, AY{min_academic_year}-{max_academic_year})",
        fontsize=14
    )
    if max_semester_number:
        ax2.set_xlim(0.5, max_semester_number + 0.5)
    else:
        ax2.set_xlim(0.5, cumulative_df["semester_number"].max() + 0.5)

    # Combine legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.show()
