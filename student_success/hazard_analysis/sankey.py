import pandas as pd
import plotly.graph_objects as go
import matplotlib.colors as mcolors
from student_success.utilityfunctions import classify_discipline

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

def classify_end_status(row, target_major_name, student_last_semester_number, student_last_semester, maximum_dataset_term):
    """
    Classifies a student's final academic status based on graduation, inactivity, or most recent discipline.

    Parameters:
    -----------
    row : pandas.Series
        A row of student data with fields including 'flag_graduation', 'major_term_name', 'discipline', and 'semester_number'.
    target_major_name : str
        The major of interest (e.g., 'Biology') used to distinguish between same-major and other-major graduation.
    student_last_semester_number : dict
        A dictionary mapping student_ID to their last recorded semester_number.
    student_last_semester : dict
        A dictionary mapping student_ID to their last recorded demographics_term.
    maximum_dataset_term : int
        The maximum demographics_term in the dataset, used to infer student inactivity.

    Returns:
    --------
    str
        A classification string such as 'Graduated Biology', 'Graduated Other', 'Left College', or a discipline name.
    """

    if row['flag_graduation'] == 1:
        if row['major_term_name'] == target_major_name:
            return f'Graduated {target_major_name}'
        else:
            return 'Graduated Other'
    elif row['semester_number'] == student_last_semester_number[row['student_ID']] and \
            ((maximum_dataset_term - student_last_semester[row['student_ID']]) > 4):
        return 'Left College'
    else:
        return row['discipline'] if pd.notna(row['discipline']) else 'Unknown Discipline'

def create_sankey_plot(data, major, plot_title, output_filename=None):
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

    print(f"Unique Students: {data['student_ID'].nunique()}")

    # TODO: parameterize somehow in success_metrics.utils.constants.py
    data['curriculum'] = pd.Categorical(data['major_term_name'], categories=[
        'Biology', 'Psychology', 'Interdisciplinary Studies', 'Computer Science', 'Other',
        'Exercise Science', 'Chemistry', 'Nursing', 'Neuroscience',
        f'Graduated {major}', 'Graduated Other', 'Left College'], ordered=True)

    student_last_semester_number = data.groupby('student_ID')['semester_number'].max().to_dict()
    student_last_semester = data.groupby('student_ID')['demographics_term'].max().to_dict()

    data['discipline'] = data['major_term'].apply(classify_discipline)

    data['end_status'] = data.apply(
        lambda row: classify_end_status(
            row, target_major_name=major,
            student_last_semester_number=student_last_semester_number,
            student_last_semester=student_last_semester,
            maximum_dataset_term=data['demographics_term'].max()),
        axis=1)

    data = data.sort_values(by=['student_ID', 'semester_number', 'curriculum'])

    # TODO: parameterize
    custom_color_map = {
        f'{major}': "#88CCEE", 'Other STEM': "#DDCC77", 'STEM-Related': "#117733",
        'Non-STEM': "#44AA99", f'Graduated {major}': "#332288",
        'Graduated Other': "#882255", 'Left College': "#CC6677",
        'Interdisciplinary Studies': "#888888"
    }

    end_statuses = [f"Graduated {major}", "Graduated Other", "Left College"]
    end_status_colors = ["#332288", "#882255", "#CC6677"]

    # TODO: parameterize
    disciplines = [f"{major}", "Other STEM", "STEM-Related", "Non-STEM", "Interdisciplinary Studies"]
    disciplines_colors = ["#88CCEE", "#DDCC77", "#117733", "#44AA99", "#888888"]

    unique_curriculum = data['discipline'].unique()
    nodes = [f"Graduated {major}", "Graduated Other", "Left College"]
    for sem in data['semester_number'].unique():
        for curr in unique_curriculum:
            if curr not in nodes:
                nodes.append(f"{curr} - Sem {sem}")

    links = {'source': [], 'target': [], 'value': [], 'color': [], 'students': []}
    students_reaching_final_status = set()

    for student in data['student_ID'].unique():
        student_data = data[data['student_ID'] == student]

        if len(student_data) == 1:
            source_curriculum = student_data.iloc[0]['discipline']
            source_sem = student_data.iloc[0]['semester_number']
            end_status = student_data.iloc[0]['end_status']
            source_node = nodes.index(f"{source_curriculum} - Sem {source_sem}")
            target_node = nodes.index(end_status)

            links['source'].append(source_node)
            links['target'].append(target_node)
            links['value'].append(1)
            links['students'].append(student)
            hex_color = custom_color_map.get(end_status, "#888888")
            links['color'].append(hex_to_rgba(hex_color))

        else:
            for i in range(len(student_data) - 1):
                source_curriculum = student_data.iloc[i]['discipline']
                target_curriculum = student_data.iloc[i + 1]['discipline']
                source_sem = student_data.iloc[i]['semester_number']
                target_sem = student_data.iloc[i + 1]['semester_number']
                source_node = nodes.index(f"{source_curriculum} - Sem {source_sem}")

                if i == len(student_data) - 2:
                    target_curriculum = student_data.iloc[i + 1]['end_status']
                    if target_curriculum not in nodes:
                        nodes.append(target_curriculum)
                    target_node = nodes.index(target_curriculum)
                else:
                    target_node = nodes.index(f"{target_curriculum} - Sem {target_sem}")

                if source_node == target_node and target_node not in [nodes.index(s) for s in end_statuses]:
                    continue

                links['source'].append(source_node)
                links['target'].append(target_node)
                links['value'].append(1)
                links['students'].append(student)
                hex_color = custom_color_map.get(target_curriculum.split(' - ')[0], "#888888")
                links['color'].append(hex_to_rgba(hex_color))

                if target_curriculum in end_statuses:
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
            color=[custom_color_map.get(node.split(' - ')[0], "#888888") for node in nodes],
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

    for i, discipline in enumerate(disciplines):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(size=100, color=disciplines_colors[i]), name=discipline))

    fig.update_layout(
        title_text=plot_title,
        font_size=20,
        height=1000,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", x=0.2, xanchor="center", y=-0.2,
                    tracegroupgap=5, itemwidth=70, font=dict(size=24)),
        yaxis=dict(showticklabels=False),
        xaxis=dict(showticklabels=False),
        annotations=[]
    )

    fig.show()
    if output_filename:
        fig.write_html(output_filename)
