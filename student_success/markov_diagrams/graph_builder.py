import pydot
import matplotlib.pyplot as plt
### helper functions
# def create_course_nodes(course_name, include_did_not_take_next=False, node_pie=False, pie_data=None, graph=None):
#     """
#     Creates labeled nodes for a course and its outcomes in a pydot graph.
#
#     Depending on the parameters, this function adds a main course node (optionally with a demographic pie chart image),
#     as well as nodes for "Pass", "DFW", "Retake", and optionally "Did Not Take Next".
#
#     Parameters
#     ----------
#     course_name : str
#         Name of the course to use in node labels.
#     include_did_not_take_next : bool, optional
#         Whether to include a "Did Not Take Next" outcome node (default is False).
#     node_pie : bool, optional
#         Whether to include a pie chart image inside the course node (default is False).
#     pie_data : dict, optional
#         Dictionary mapping color names to proportions, used to create pie chart (only if node_pie is True).
#     graph : pydot.Dot, optional
#         The graph to which nodes should be added.
#
#     Returns
#     -------
#     dict
#         Dictionary of pydot.Node objects keyed by role ('course', 'pass', 'dfw', 'retake', 'did_not_take_next').
#     """
#
#     import os
#
#     nodes = {}
#     course_node = pydot.Node(course_name, shape="box", label=course_name)
#     nodes["course"] = course_node
#
#     # Create the main course node (always a box)
#     if graph and not node_pie:
#         graph.add_node(course_node)
#
#     # Optional pie chart node
#     if node_pie and pie_data and graph:
#         temp_dir = os.getcwd() + '\\temp\\'
#         image_path = f"{temp_dir}/{course_name.replace(' ', '_')}.png"
#         save_pie_chart(pie_data, image_path)
#
#         course_node = create_course_node_with_image(course_name, image_path)
#         graph.add_node(course_node)
#
#     # Add outcome nodes
#     nodes["pass"] = pydot.Node(f"Pass {course_name}", label="Pass")
#     nodes["dfw"] = pydot.Node(f"DFW {course_name}", label="DFW")
#     nodes["retake"] = pydot.Node(f"Retake {course_name}", label="Retake")
#
#     if include_did_not_take_next:
#         nodes["did_not_take_next"] = pydot.Node(f"Did Not Take Next {course_name}", label="Did Not Take Next")
#
#     return nodes

def create_course_nodes(course_name, include_did_not_take_next=False, node_pie=False, pie_data=None, graph=None):
    """
    Creates labeled nodes for a course and its outcomes in a pydot graph.

    Optionally adds demographic pie charts to multiple nodes (course, pass, DFW, retake).

    Parameters
    ----------
    course_name : str
        Name of the course to use in node labels.
    include_did_not_take_next : bool, optional
        Whether to include a "Did Not Take Next" outcome node.
    node_pie : bool, optional
        If True, allows pie charts to be used.
    pie_data : dict, optional
        Dictionary mapping node roles ('course', 'DFW', etc.) to pie chart color proportions.
    graph : pydot.Dot, optional
        The graph to which nodes will be added.

    Returns
    -------
    dict
        Dictionary of pydot.Node objects keyed by role.
    """
    import os

    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    roles = ["course", "pass", "DFW", "retake"]
    if include_did_not_take_next:
        roles.append("did_not_take_next")

    nodes = {}

    for role in roles:
        if role == "course":
            label = course_name
            node_name = course_name  # don't repeat it
        else:
            label = role
            node_name = f"{label} {course_name}"

        if node_pie and pie_data and role in pie_data:
            image_path = os.path.join(temp_dir, f"{node_name.replace(' ', '_')}.png")
            save_pie_chart(pie_data[role], image_path)
            node = create_node_with_image(node_name=node_name, label=label, image_path=image_path)
        else:
            node = pydot.Node(name = node_name, label=label)

        nodes[role] = node
        if graph:
            graph.add_node(node)

    return nodes


def add_course_edges(graph, nodes, stats, include_did_not_take_next=False):
    """
    Adds outcome edges to a course graph, labeled with performance statistics.

    Edges are drawn from the course node to the "Pass" and "DFW" nodes,
    from "DFW" to "Retake", and from "Retake" to both "Pass" and "Did Not Take Next"
    based on provided summary stats.

    Parameters
    ----------
    graph : pydot.Dot
        The graph to which edges should be added.
    nodes : dict
        Dictionary of node objects created by `create_course_nodes()`.
    stats : dict
        Dictionary containing performance statistics (e.g., DFW rate, repeat pass rate).
    include_did_not_take_next : bool, optional
        Whether to include edges to a "Did Not Take Next" node (default is False).
    """

    graph.add_edge(pydot.Edge(nodes['course'], nodes['pass'],
                              label=f"{stats['first_pass_proportion']:.3f} ({stats['first_pass_number']})"))
    graph.add_edge(pydot.Edge(nodes['course'], nodes['DFW'],
                              label=f"{stats['first_DFW_proportion']:.3f} ({stats['first_DFW_number']})"))
    graph.add_edge(pydot.Edge(nodes['DFW'], nodes['retake'],
                              label=f"{stats['proportion_DFW_repeat']:.3f} ({stats['second_attempt_number']})"))
    graph.add_edge(pydot.Edge(nodes['retake'], nodes['pass'],
                              label=f"{stats['second_pass_proportion']:.3f} ({stats['second_pass_number']})"))

    if include_did_not_take_next:
        graph.add_edge(pydot.Edge(nodes['DFW'], nodes['did_not_take_next'],
                                  label=f"{1 - stats['proportion_DFW_repeat']:.3f} ({stats['first_DFW_number'] - stats['second_attempt_number']})"))
        graph.add_edge(pydot.Edge(nodes['retake'], nodes['did_not_take_next'],
                                  label=f"{stats['second_DFW_proportion']:.3f} ({stats['second_DFW_number']})"))

def add_alternate_entry(graph, course_name, alt_entry_count):
    """
    Adds a node and edge to represent students entering a course without taking the prior prerequisite.

    Parameters
    ----------
    graph : pydot.Dot
        The graph to which the alternate entry node and edge will be added.
    course_name : str
        Name of the course receiving alternate entries.
    alt_entry_count : int
        Number of students entering without prior course completion.
    """

    node = pydot.Node(name = f"Alternate Entry to {course_name}", label="Alternate Entry")
    graph.add_node(node)
    graph.add_edge(pydot.Edge(node, pydot.Node(course_name), label=f"{alt_entry_count}"))

def get_combined_course_df(df, ids_1, ids_2):
    """
    Returns a filtered DataFrame including only students present in at least one of two ID sets.

    Useful when combining students who progressed from one course to the next and those who entered from alternate pathways.

    Parameters
    ----------
    df : pandas.DataFrame
        The full dataset to filter.
    ids_1 : iterable
        Set of student_IDs (e.g., those who took the prerequisite).
    ids_2 : iterable
        Set of student_IDs (e.g., alternate entries).

    Returns
    -------
    pandas.DataFrame
        Subset of `df` containing rows where student_ID is in either `ids_1` or `ids_2`.
    """

    return df[df['student_ID'].isin(set(ids_1) | set(ids_2))]


def get_earliest_major(df):
    """
    Determines each student's earliest major and merges it into the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with at least ['student_ID', 'course_term', 'major_matriculation'] columns.

    Returns
    -------
    pandas.DataFrame
        Original dataframe with a new 'major_matriculation' column set to the earliest observed value.

    Notes: helper function that may be useful at some point...move to utils or delete?
    """
    df_sorted = df.sort_values(by=['student_ID', 'course_term'])
    earliest = df_sorted.groupby('student_ID').first()['major_term_earliest']
    df_merged = df.merge(earliest, how='left', on='student_ID', suffixes=('', '_Earliest'))
    df_merged['major_matriculation'] = df_merged['major_matriculation_Earliest'].fillna(df_merged['major_matriculation'])
    return df_merged.drop(columns=['major_matriculation_Earliest'])




# def course_sequence_analysis(course_sequence, df, major_matriculation_column = 'major_term_earliest',
#                              target_major_code = None, node_pie=False, demographics_flag_col = None):
#     """
#     Generates a flow diagram showing student progression through a sequence of courses.
#
#     The diagram includes labeled nodes and edges representing outcomes and transitions,
#     with optional pie chart embeddings to visualize demographic breakdowns.
#
#     Parameters
#     ----------
#     course_sequence : list of str
#         Ordered list of course titles to include in the sequence.
#     df : pandas.DataFrame
#         Dataset containing course attempts, grades, and demographics.
#     major_matriculation_column : str, optional
#         Column name indicating students' earliest major (default 'major_term_earliest').
#     target_major_code : str, optional
#         If provided, limits analysis to students with this major.
#     node_pie : bool, optional
#         Whether to embed demographic pie charts in course nodes (default False).
#     demographics_flag_col : str, optional
#         Column name for a binary or categorical demographic used in pie charts (required if node_pie is True).
#
#     Returns
#     -------
#     None
#         Writes a PNG file of the course sequence diagram and displays it with matplotlib.
#     """
#
#     import pydot
#
#     from student_success.markov_diagrams.course_flows import (
#         analyze_course, calculate_alternate_entry, calculate_progression_to_next_course
#     )
#
#     def filter_kwargs(include_node_pie=False):
#         kwargs = {
#             'major_matriculation_column': major_matriculation_column
#         }
#         if target_major_code is not None:
#             kwargs['target_major_code'] = target_major_code
#         if include_node_pie:
#             kwargs['node_pie'] = node_pie
#         if node_pie:
#             kwargs['demographics_flag_col'] = demographics_flag_col
#         return kwargs
#
#     if not node_pie and demographics_flag_col is not None:
#         raise ValueError("You specified a demographics_flag_col, but node_pie=False. "
#                          "Either enable pie charts or remove the demographics_col.")
#     if node_pie and demographics_flag_col is None:
#         raise ValueError("You specified node_pie = True but did not provide a demographics_flag_col. "
#                          "Either disable pie charts or specify demographics_flag_col.")
#
#
#
#     graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
#     previous_pass_node = None
#
#     for index, course_name in enumerate(course_sequence):
#         is_last = index == len(course_sequence) - 1
#         is_first = index == 0
#         include_did_not_take = index < len(course_sequence) - 1
#
#         print(f"Index: {index}, is_last: {is_last}, is_first: {is_first}")
#
#         if is_first and not is_last:
#             if node_pie:
#                 descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=True))
#                 pie_data = descriptives.get("first_attempt_demographic_proportions")
#             else:
#                 descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=False))
#                 pie_data = None
#
#             nodes = create_course_nodes(
#                 course_name,
#                 include_did_not_take_next=include_did_not_take,
#                 node_pie=node_pie,
#                 pie_data=pie_data,
#                 graph = graph)
#
#             for node in nodes.values():
#                 graph.add_node(node)
#
#             progression = calculate_progression_to_next_course(
#                 course_name,
#                 course_sequence[index + 1],
#                 df,
#                 major_matriculation_column=major_matriculation_column,
#                 target_major_code=target_major_code if target_major_code else None
#             )
#
#             print("Next course name : ", course_sequence[index + 1])
#             print("Number taking next : ", progression['number_taking_next'])
#             graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
#                                       label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))
#
#         else:
#             prerequisite = course_sequence[index - 1]
#             print("The prerequisite course name is", prerequisite, "and current course is", course_name)
#
#             alt_entry = calculate_alternate_entry(
#                 current_course = course_name, prior_course = prerequisite, df = df,
#                 target_major_code = target_major_code, major_matriculation_column = major_matriculation_column)
#             add_alternate_entry(graph, course_name, alt_entry['n_without_prior_pass'])
#             students_in_alternate_entry = alt_entry['alt_entry_ids']
#
#             prereq_result = calculate_progression_to_next_course(
#                 prerequisite,
#                 course_name,
#                 df,
#                 major_matriculation_column=major_matriculation_column,
#                 target_major_code=target_major_code if target_major_code else None
#             )
#
#             graph.add_edge(pydot.Edge(previous_pass_node.get_name(), course_name,
#                                       label=f"{prereq_result['proportion_taking_next']:.3f} ({prereq_result['number_taking_next']})"))
#
#             students_who_did_take_next = prereq_result['students_who_did_take_next']
#             combined_df = get_combined_course_df(df, students_who_did_take_next, students_in_alternate_entry)
#             descriptives = analyze_course(course_name, combined_df, **filter_kwargs(include_node_pie=True))
#
#             # Get the proportions for course demographics if node_pie == True
#             if node_pie and descriptives:
#                 pie_data = descriptives.get("first_attempt_demographic_proportions")
#                 print(pie_data)
#             else:
#                 pie_data = None
#
#             nodes = create_course_nodes(
#                 course_name,
#                 include_did_not_take_next=include_did_not_take,
#                 node_pie=node_pie,
#                 pie_data=pie_data,
#                 graph=graph)
#
#             for node in nodes.values():
#                  graph.add_node(node)
#
#             # move to next course
#             if not is_last:
#                 next_course = course_sequence[index + 1]
#                 print("Course name : ", course_name)
#                 print("Next course name : ", next_course)
#
#                 progression = calculate_progression_to_next_course(course_name, next_course, df, **filter_kwargs())
#
#                 print("Number not taking next : ", progression['number_not_taking_next'])
#                 graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
#                                           label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))
#
#         print(descriptives)
#
#         add_course_edges(graph, nodes, descriptives, include_did_not_take_next=include_did_not_take)
#         previous_pass_node = nodes['pass']
#
#     graph.set("nodesep", "1.0")
#     image_filename = "course_sequence_attempts_graph.png"
#     graph.write(image_filename, format ="png", prog="dot", encoding = "utf-8")
#     graph.set_graph_defaults(dpi = "300")
#     # graph.write_raw("debug_graph.dot")
#
#     fig = plt.figure(figsize=(6, 6), dpi = 300)
#
#     if target_major_code:
#         fig.suptitle(f"Course Sequence Analysis for {target_major_code} Majors", fontsize=12)
#     else:
#         fig.suptitle(f"Course Sequence Analysis (no major filter applied)", fontsize=12)
#     ax = fig.add_subplot(111)
#     ax.axis('off')
#     img = plt.imread(image_filename)
#     ax.imshow(img)
#     plt.show()


def course_sequence_analysis(course_sequence, df, major_matriculation_column = 'major_term_earliest',
                             target_major_code = None, node_pie=False, demographics_flag_col = None):
    """
    Generates a flow diagram showing student progression through a sequence of courses.

    The diagram includes labeled nodes and edges representing outcomes and transitions,
    with optional pie chart embeddings to visualize demographic breakdowns.

    Parameters
    ----------
    course_sequence : list of str
        Ordered list of course titles to include in the sequence.
    df : pandas.DataFrame
        Dataset containing course attempts, grades, and demographics.
    major_matriculation_column : str, optional
        Column name indicating students' earliest major (default 'major_term_earliest').
    target_major_code : str, optional
        If provided, limits analysis to students with this major.
    node_pie : bool, optional
        Whether to embed demographic pie charts in course nodes (default False).
    demographics_flag_col : str, optional
        Column name for a binary or categorical demographic used in pie charts (required if node_pie is True).

    Returns
    -------
    None
        Writes a PNG file of the course sequence diagram and displays it with matplotlib.
    """

    import pydot

    from student_success.markov_diagrams.course_flows import (
        analyze_course, calculate_alternate_entry, calculate_progression_to_next_course
    )

    def filter_kwargs(include_node_pie=False):
        kwargs = {
            'major_matriculation_column': major_matriculation_column
        }
        if target_major_code is not None:
            kwargs['target_major_code'] = target_major_code
        if include_node_pie:
            kwargs['node_pie'] = node_pie
        if node_pie:
            kwargs['demographics_flag_col'] = demographics_flag_col
        return kwargs

    if not node_pie and demographics_flag_col is not None:
        raise ValueError("You specified a demographics_flag_col, but node_pie=False. "
                         "Either enable pie charts or remove the demographics_col.")
    if node_pie and demographics_flag_col is None:
        raise ValueError("You specified node_pie = True but did not provide a demographics_flag_col. "
                         "Either disable pie charts or specify demographics_flag_col.")



    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    previous_pass_node = None

    for index, course_name in enumerate(course_sequence):
        is_last = index == len(course_sequence) - 1
        is_first = index == 0
        include_did_not_take = index < len(course_sequence) - 1

        print(f"Index: {index}, is_last: {is_last}, is_first: {is_first}")

        if is_first and not is_last:
            if node_pie:
                descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=True))
                pie_data = {
                    "course": descriptives.get("first_attempt_demographic_proportions"),
                    "DFW": descriptives.get("first_DFW_demographic_proportions")
                    # optionally add "pass", "retake", etc.
                }

            else:
                descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=False))
                pie_data = None

            nodes = create_course_nodes(
                course_name,
                include_did_not_take_next=include_did_not_take,
                node_pie=node_pie,
                pie_data=pie_data,
                graph = graph)

            for node in nodes.values():
                graph.add_node(node)

            progression = calculate_progression_to_next_course(
                course_name,
                course_sequence[index + 1],
                df,
                major_matriculation_column=major_matriculation_column,
                target_major_code=target_major_code if target_major_code else None
            )

            print("Next course name : ", course_sequence[index + 1])
            print("Number taking next : ", progression['number_taking_next'])
            graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
                                      label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))

        else:
            prerequisite = course_sequence[index - 1]
            print("The prerequisite course name is", prerequisite, "and current course is", course_name)

            alt_entry = calculate_alternate_entry(
                current_course = course_name, prior_course = prerequisite, df = df,
                target_major_code = target_major_code, major_matriculation_column = major_matriculation_column)
            add_alternate_entry(graph, course_name, alt_entry['n_without_prior_pass'])
            students_in_alternate_entry = alt_entry['alt_entry_ids']

            prereq_result = calculate_progression_to_next_course(
                prerequisite,
                course_name,
                df,
                major_matriculation_column=major_matriculation_column,
                target_major_code=target_major_code if target_major_code else None
            )

            graph.add_edge(pydot.Edge(previous_pass_node.get_name(), course_name,
                                      label=f"{prereq_result['proportion_taking_next']:.3f} ({prereq_result['number_taking_next']})"))

            students_who_did_take_next = prereq_result['students_who_did_take_next']
            combined_df = get_combined_course_df(df, students_who_did_take_next, students_in_alternate_entry)
            descriptives = analyze_course(course_name, combined_df, **filter_kwargs(include_node_pie=True))

            # Get the proportions for course demographics if node_pie == True
            if node_pie and descriptives:
                pie_data = {
                    "course": descriptives.get("first_attempt_demographic_proportions"),
                    "DFW": descriptives.get("first_DFW_demographic_proportions")
                    # optionally add "pass", "retake", etc.
                }
                print(pie_data)
            else:
                descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=False))
                pie_data = None

            nodes = create_course_nodes(
                course_name,
                include_did_not_take_next=include_did_not_take,
                node_pie=node_pie,
                pie_data=pie_data,
                graph=graph)

            for node in nodes.values():
                 graph.add_node(node)

            # move to next course
            if not is_last:
                next_course = course_sequence[index + 1]
                print("Course name : ", course_name)
                print("Next course name : ", next_course)

                progression = calculate_progression_to_next_course(course_name, next_course, df, **filter_kwargs())

                print("Number not taking next : ", progression['number_not_taking_next'])
                graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
                                          label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))

        print(descriptives)

        add_course_edges(graph, nodes, descriptives, include_did_not_take_next=include_did_not_take)
        previous_pass_node = nodes['pass']

    graph.set("nodesep", "1.0")
    image_filename = "course_sequence_attempts_graph.png"
    graph.write(image_filename, format ="png", prog="dot", encoding = "utf-8")
    graph.set_graph_defaults(dpi = "300")
    # graph.write_raw("debug_graph.dot")

    fig = plt.figure(figsize=(6, 6), dpi = 300)

    if target_major_code:
        fig.suptitle(f"Course Sequence Analysis for {target_major_code} Majors", fontsize=12)
    else:
        fig.suptitle(f"Course Sequence Analysis (no major filter applied)", fontsize=12)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()

def save_pie_chart(pie_data, filepath):
    """
    Generates and saves a pie chart image from demographic proportions.

    Parameters
    ----------
    pie_data : dict
        Dictionary mapping color names to proportions (e.g., {'green': 0.6, 'blue': 0.4}).
    filepath : str
        Full path where the PNG image should be saved.
    """

    colors = list(pie_data.keys())
    values = list(pie_data.values())

    fig, ax = plt.subplots(figsize=(0.9, 0.9), dpi=100)
    ax.pie(values, colors=colors, wedgeprops=dict(edgecolor='black'))

    # Add circular outline
    circle = plt.Circle((0, 0), 1.0, transform=ax.transData, fill=False, color='black', linewidth=1)
    ax.add_patch(circle)

    ax.axis('equal')  # Keep circular

    plt.savefig(filepath, transparent=True, bbox_inches='tight', pad_inches=0.15)
    plt.close()

def create_node_with_image(node_name, image_path, label = None):
    """
    Creates a box-shaped pydot node with an embedded pie chart image and a label.

    Parameters
    ----------
    node_name : str
        Identifier for the node
    image_path : str
        Path to the PNG image to embed within the node.
    label : str (optional)
        Label to display below the pie chart image.

    Returns
    -------
    pydot.Node
        A box-shaped node embedding an image and labeled with the course name.
    """

    return pydot.Node(
        name=node_name,
        label=f"\n\n{label if label else node_name}",
        shape="box",
        image=image_path,
        labelloc="b",           # optional: label below the image
        # imagescale="true",
        fontsize="12",
        # width="1.2",            # size adjustments
        # height="1.4",
        fixedsize="false",
        margin = "0.1, 0.4"
    )