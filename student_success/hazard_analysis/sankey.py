import pandas as pd
import warnings
import plotly.graph_objects as go
import matplotlib.colors as mcolors
from student_success.utils.time_utils import calculate_semester_interval, standardize_to_term_code
from student_success.metrics.flagging import (
    classify_graduation_status,
    classify_graduation_in_major
)

from student_success.utils.constants import (
    SANKEY_DISCIPLINE_GROUPS,
    SANKEY_DISCIPLINE_COLOR_MAP
)


def hex_to_rgba(hex_color, alpha=0.4):
    """
    Converts a hex color string to an RGBA string with the specified alpha transparency.

    Parameters:
    -----------
    hex_color : str
        A hex color code (e.g., '#88CCEE').
    alpha : float, optional
        Transparency level from 0 (fully transparent) to 1 (fully opaque). Default is 0.4.

    Returns:
    --------
    str
        An RGBA color string (e.g., 'rgba(136, 204, 238, 0.4)').
    """

    rgba = mcolors.to_rgba(hex_color, alpha=alpha)
    return f"rgba({int(rgba[0] * 255)}, {int(rgba[1] * 255)}, {int(rgba[2] * 255)}, {rgba[3]})"

def wrap_plot_title(title, max_length=75):
    """
    Inserts a <br> line break into the title string at the nearest space
    before the max_length character limit for improved layout in narrow displays.
    """
    if len(title) <= max_length:
        return title
    break_index = title.rfind(' ', 0, max_length)
    if break_index == -1:
        break_index = max_length
    return title[:break_index] + "<br>" + title[break_index+1:]


def create_sankey_plot(data, target_major, plot_title, output_filename=None, target_major_name = None):
    """
    Creates and displays a Sankey diagram to visualize student flow across disciplines and outcomes.

    This function generates an interactive Sankey diagram using Plotly, showing how students in a specified
    major move through different disciplines across semesters and ultimately graduate, change majors, or leave.

    Parameters:
    -----------
    data : pandas.DataFrame
        A DataFrame containing student records with columns including 'student_ID', 'major_term',
        'major_term_name', 'semester_number', 'flag_graduation', and 'demographics_term'.

    major : str
        The abbreviation of the target major (e.g., 'BIO') to highlight in the Sankey flow.

    plot_title : str
        Title to display at the top of the Sankey diagram.

    output_filename : str, optional
        If specified, saves the Sankey plot as an HTML file to this path.

    Notes:
    ------
    - This function assumes majors have been normalized (e.g., premajors replaced via PREMAJOR_TO_MAJOR_DICT; see utils.constants.py).
    - Custom color mappings and curriculum category orders are currently hard-coded.
    - Hover tooltips display transition counts, and color legends explain flows by status and discipline.
    """
    if target_major_name is None:
        target_major_name = target_major  # fallback if not provided

    print(f"Unique Students: {data['student_ID'].nunique()}")

    student_last_semester_number = data.groupby('student_ID')['semester_number'].max().to_dict()
    student_last_semester = data.groupby('student_ID')['demographics_term'].max().to_dict()

    data['discipline'] = data['major_term'].apply(lambda m: classify_sankey_discipline(m, target_major))
    data = assign_sankey_end_status(data, target_major=target_major)
    data = data.sort_values(by=['student_ID', 'semester_number'])

    custom_color_map = SANKEY_DISCIPLINE_COLOR_MAP.copy()
    custom_color_map.update({
        f'Graduated {target_major}': "#332288",
        'Graduated Other': "#882255",
        'Left College': "#CC6677"
    })

    end_statuses = [f"Graduated {target_major}", "Graduated Other", "Left College"]
    end_status_colors = ["#332288", "#882255", "#CC6677"]

    unique_disciplines = data['discipline'].unique()
    nodes = [f"Graduated {target_major}", "Graduated Other", "Left College"]
    for sem in data['semester_number'].unique():
        for disc in unique_disciplines:
            if disc not in nodes:
                nodes.append(f"{disc} - Sem {sem}")

    links = {'source': [], 'target': [], 'value': [], 'color': [], 'students': []}
    students_reaching_final_status = set()

    for student in data['student_ID'].unique():
        student_data = data[data['student_ID'] == student]

        if len(student_data) == 1:
            source_discipline = student_data.iloc[0]['discipline']
            source_sem = student_data.iloc[0]['semester_number']
            end_status = student_data.iloc[0]['end_status']
            source_node = nodes.index(f"{source_discipline} - Sem {source_sem}")
            target_node = nodes.index(end_status)

            links['source'].append(source_node)
            links['target'].append(target_node)
            links['value'].append(1)
            links['students'].append(student)
            hex_color = custom_color_map.get(end_status, "#888888")
            links['color'].append(hex_to_rgba(hex_color))

        else:
            for i in range(len(student_data) - 1):
                source_discipline = student_data.iloc[i]['discipline']
                target_discipline = student_data.iloc[i + 1]['discipline']
                source_sem = student_data.iloc[i]['semester_number']
                target_sem = student_data.iloc[i + 1]['semester_number']
                source_node = nodes.index(f"{source_discipline} - Sem {source_sem}")

                if i == len(student_data) - 2:
                    target_discipline = student_data.iloc[i + 1]['end_status']
                    if target_discipline not in nodes:
                        nodes.append(target_discipline)
                    target_node = nodes.index(target_discipline)
                else:
                    target_node = nodes.index(f"{target_discipline} - Sem {target_sem}")

                if source_node == target_node and target_node not in [nodes.index(s) for s in end_statuses]:
                    continue

                links['source'].append(source_node)
                links['target'].append(target_node)
                links['value'].append(1)
                links['students'].append(student)
                hex_color = custom_color_map.get(target_discipline.split(' - ')[0], "#888888")
                links['color'].append(hex_to_rgba(hex_color))

                if target_discipline in end_statuses:
                    students_reaching_final_status.add(student)

    links_df = pd.DataFrame(links)
    grouped_links = links_df.groupby(['source', 'target', 'color']).agg({'value': 'sum'}).reset_index()
    node_value_map = data.groupby(['discipline', 'semester_number'])['student_ID'].nunique().to_dict()
    node_labels_with_values = [f"{node}: {node_value_map.get(node, '0')} students" for node in nodes]
    grouped_links['custom_source_label'] = [nodes[s] for s in grouped_links['source']]
    grouped_links['custom_target_label'] = [nodes[t] for t in grouped_links['target']]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=0,
            thickness=20,
            line=dict(color="black", width=1),
            label=["" for _ in nodes],
            color=[custom_color_map.get(extract_node_label(node), "#888888") for node in nodes],
            hovertemplate="%{value}",
            hoverlabel=dict(bgcolor="white", font=dict(size=20))
        ),
        link=dict(
            source=grouped_links['source'],
            target=grouped_links['target'],
            value=grouped_links['value'],
            color=grouped_links['color'],
            label=["" for _ in grouped_links['source']],
            hovertemplate="%{value}",
            hoverlabel=dict(bgcolor="white", font=dict(size=20))
        )
    ))

    for i, status in enumerate(end_statuses):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(size=100, color=end_status_colors[i]), name=status))

    for discipline, color in custom_color_map.items():
        if discipline not in end_statuses:
            fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                     marker=dict(size=100, color=color),
                                     name=SANKEY_DISCIPLINE_GROUPS.get(discipline, discipline)))

    fig.update_layout(
        title = dict(
            text=wrap_plot_title(plot_title),
            x = 0.45,
            xanchor = 'center',
            font = dict(size=20)
        ),
        height=1000,
        width =1200,
        showlegend=True,
        legend=dict(
            orientation="v",
            y=1,
            x=1.02,  # places it just outside the right edge
            xanchor="left",
            yanchor="top",
            font=dict(size=16)
        ),
        yaxis=dict(showticklabels=False),
            xaxis=dict(showticklabels=False),
            annotations=[]
    )

    fig.show()
    if output_filename:
        fig.write_html(output_filename)


# refactoring on 2025-06-05
def assign_sankey_end_status(df, target_major, max_term=None, inactivity_gap=4):
    """
    Classifies end status for Sankey plots: Graduated [target_major], Graduated Other, Left College, or last known discipline.

    Parameters
    ----------
    df : pd.DataFrame
        Student-term level dataset.
    target_major_name : str
        e.g., 'BIO'
    max_term : int, optional
        Maximum demographics_term to evaluate inactivity. If None, computed from df.
    inactivity_gap : int
        Term gap threshold to flag students as inactive (default = 4).

    Returns
    -------
    df : pd.DataFrame
        Original df with an added 'end_status' column for Sankey plotting.

    Notes
    -----
    If your dataset includes custom-coded composite Spring+Summer terms (e.g., 2019.11),
    these are internally standardized to YYYY05 for interval calculations.

    To ensure correct interpretation, you must pre-filter out "Summer only"
    records (e.g., 2019.01) when using combined Spring+Summer composite logic.
    Otherwise, distinct student trajectories may be conflated in downstream analyses.
    """

    df = df.copy()

    if df['demographics_term'].apply(lambda x: isinstance(x, float) and str(x).endswith(".11")).any() and \
       df['demographics_term'].apply(lambda x: isinstance(x, float) and str(x).endswith(".01")).any():
        warnings.warn(
            "Dataset includes BOTH composite (.11) and summer-only (.01) terms — consider filtering to avoid conflation."
        )

    # Standardize terms
    df['standard_term'] = df['demographics_term'].apply(standardize_to_term_code)

    if max_term is None:
        max_term = df['demographics_term'].max()
    max_term_standard = standardize_to_term_code(max_term)

    # Graduation flags
    df['flag_graduation'] = classify_graduation_status(df)
    df['flag_graduation_in_major'] = classify_graduation_in_major(df, target_major=target_major)

    # Get last standardized term and discipline by student
    last_term_by_student = df.groupby('student_ID')['standard_term'].max()
    discipline_by_student = df.sort_values('demographics_term').groupby('student_ID')['discipline'].last()

    def classify(row):
        sid = row['student_ID']
        last_term = last_term_by_student[sid]
        discipline = discipline_by_student.get(sid, 'Unknown Discipline')

        if row['standard_term'] != last_term:
            return None  # Only classify in last term

        if row['flag_graduation'] == 1:
            if row['flag_graduation_in_major'] == 1:
                return f'Graduated {target_major}'
            else:
                return 'Graduated Other'

        elif calculate_semester_interval(
            semester_A=last_term,
            semester_B=max_term_standard
        ) > inactivity_gap:
            return 'Left College'

        else:
            return discipline if pd.notna(discipline) else 'Unknown Discipline'

    df['end_status'] = df.apply(classify, axis=1)
    return df

def classify_sankey_discipline(major_abbrev, target_major):
    if major_abbrev == target_major:
        return 'Target Major'
    return SANKEY_DISCIPLINE_GROUPS.get(major_abbrev, 'Unknown')

def extract_node_label(node):
    return node.split(' - ')[0] if ' - Sem' in node else node