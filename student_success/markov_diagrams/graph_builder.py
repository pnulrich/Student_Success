import pydot
import matplotlib.pyplot as plt
### helper functions
def create_course_nodes(course_name, include_did_not_take_next=False, node_pie=False, pie_data=None, graph=None):
    """
    Creates labeled nodes for a course and its outcomes in a pydot graph.

    Depending on the parameters, this function adds a main course node (optionally with a demographic pie chart image),
    as well as nodes for "Pass", "DFW", "Retake", and optionally "Did Not Take Next".

    Parameters
    ----------
    course_name : str
        Name of the course to use in node labels.
    include_did_not_take_next : bool, optional
        Whether to include a "Did Not Take Next" outcome node (default is False).
    node_pie : bool, optional
        Whether to include a pie chart image inside the course node (default is False).
    pie_data : dict, optional
        Dictionary mapping color names to proportions, used to create pie chart (only if node_pie is True).
    graph : pydot.Dot, optional
        The graph to which nodes should be added.

    Returns
    -------
    dict
        Dictionary of pydot.Node objects keyed by role ('course', 'pass', 'dfw', 'retake', 'did_not_take_next').
    """

    import os

    nodes = {}
    course_node = pydot.Node(course_name, shape="box", label=course_name)
    nodes["course"] = course_node

    # Create the main course node (always a box)
    if graph and not node_pie:
        graph.add_node(course_node)

    # Optional pie chart node
    if node_pie and pie_data and graph:
        temp_dir = os.getcwd() + '\\temp\\'
        image_path = f"{temp_dir}/{course_name.replace(' ', '_')}.png"
        save_pie_chart(pie_data, image_path)

        course_node = create_course_node_with_image(course_name, image_path)
        graph.add_node(course_node)

        # # add course node
        # graph.add_node(course_node)
        #
        # #create pie chart node
        # pie_node_name = f"{course_name}_pie"
        # wedges = [f"{color};{proportion:.2f}" for color, proportion in pie_data.items()]
        # fillcolor = ":".join(wedges)
        #
        # pie_node = pydot.Node(
        #     pie_node_name,
        #     label="",
        #     shape="circle",
        #     style="wedged",
        #     fillcolor=fillcolor,
        #     width="0.5",
        #     height="0.5",
        #     penwidth="0.5",
        #     color="gray",
        #     margin =0
        # )
        #
        # # add pie chart node
        # graph.add_node(pie_node)
        # # Invisible edge to force layout
        # graph.add_edge(pydot.Edge(course_name, pie_node_name, style="invis", weight=100))
        # subgraph = pydot.Subgraph(rank='same')
        # subgraph.add_node(course_node)
        # subgraph.add_node(pie_node)
        # graph.add_subgraph(subgraph)

    # Add outcome nodes
    nodes["pass"] = pydot.Node(f"Pass {course_name}", label="Pass")
    nodes["dfw"] = pydot.Node(f"DFW {course_name}", label="DFW")
    nodes["retake"] = pydot.Node(f"Retake {course_name}", label="Retake")

    if include_did_not_take_next:
        nodes["did_not_take_next"] = pydot.Node(f"Did Not Take Next {course_name}", label="Did Not Take Next")

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
    graph.add_edge(pydot.Edge(nodes['course'], nodes['dfw'],
                              label=f"{stats['first_DFW_proportion']:.3f} ({stats['first_DFW_number']})"))
    graph.add_edge(pydot.Edge(nodes['dfw'], nodes['retake'],
                              label=f"{stats['proportion_DFW_repeat']:.3f} ({stats['second_attempt_number']})"))
    graph.add_edge(pydot.Edge(nodes['retake'], nodes['pass'],
                              label=f"{stats['second_pass_proportion']:.3f} ({stats['second_pass_number']})"))

    if include_did_not_take_next:
        graph.add_edge(pydot.Edge(nodes['dfw'], nodes['did_not_take_next'],
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

    node = pydot.Node(f"Alternate Entry to {course_name}", label="Alternate Entry")
    graph.add_node(node)
    graph.add_edge(pydot.Edge(node, pydot.Node(course_name), label=f"{alt_entry_count}"))
    # graph.add_edge(pydot.Edge(node, course_name, label=f"{alt_entry_count}"))

def get_combined_course_df(df, ids_1, ids_2):
    """
    Returns a filtered dataframe containing rows for a union of two student ID sets.

    Parameters
    ----------
    df : pandas.DataFrame
        The full course dataset.
    ids_1 : iterable
        First set of student IDs.
    ids_2 : iterable
        Second set of student IDs.

    Returns
    -------
    pandas.DataFrame
        Subset of `df` where student_ID is in either `ids_1` or `ids_2`.
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




def course_sequence_analysis(course_sequence, df, major_matriculation_column = 'major_term_earliest',
                             target_major_code = None, node_pie=False):
    """
    Constructs a flow diagram representing student progression across a sequence of courses.

    Includes demographic breakdowns if `node_pie` is enabled. Handles alternate entries, drop-off,
    and repeat behavior using custom edge logic and summary statistics.

    Parameters
    ----------
    course_sequence : list of str
        Ordered list of course names to include in the flow sequence.
    df : pandas.DataFrame
        Input dataset with course, grade, and student demographic data.
    major_matriculation_column : str, optional
        Column name indicating each student's major at matriculation.
    target_major_code : str or None, optional
        If specified, restrict analysis to students with this major.
    node_pie : bool, optional
        Whether to embed demographic pie charts in course nodes.

    Returns
    -------
    None
        Writes out a PNG image of the course flow diagram and displays it using matplotlib.
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
        return kwargs

    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    previous_pass_node = None

    for index, course_name in enumerate(course_sequence):


        is_last = index == len(course_sequence) - 1
        is_first = index == 0
        include_did_not_take = index < len(course_sequence) - 1

        print(f"Index: {index}, is_last: {is_last}, is_first: {is_first}")


        # Create and add course nodes
        #nodes = create_course_nodes(course_name, include_did_not_take_next=include_did_not_take)
        #for node in nodes.values():
        #    graph.add_node(node)

        if is_first and not is_last:
            descriptives = analyze_course(course_name, df, **filter_kwargs(include_node_pie=True))
            print(f"\n\nWe are in is_first and is_last condition: {descriptives.get('first_attempt_proportions')}")

            # Get the proportions for course demographics if node_pie == True
            if node_pie and descriptives:
                pie_data = descriptives.get("first_attempt_proportions")
            else:
                pie_data = None

            nodes = create_course_nodes(
                course_name,
                include_did_not_take_next=include_did_not_take,
                node_pie=node_pie,
                pie_data=pie_data,
                graph = graph)

            for node in nodes.values():
                graph.add_node(node)

            progression = calculate_progression_to_next_course(course_name, course_sequence[index + 1], df,
                                                               **filter_kwargs())
            print("Next course name : ", course_sequence[index + 1])
            print("Number taking next : ", progression['number_taking_next'])
            graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
                                      label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))

        else:
            prerequisite = course_sequence[index - 1]
            print("The prerequisite course name is", prerequisite, "and current course is", course_name)

            alt_entry = calculate_alternate_entry(course_name, prerequisite, df, **filter_kwargs())
            add_alternate_entry(graph, course_name, alt_entry['n_without_prior_pass'])
            students_in_alternate_entry = alt_entry['alt_entry_ids']

            prereq_result = calculate_progression_to_next_course(prerequisite, course_name, df, **filter_kwargs())

            graph.add_edge(pydot.Edge(previous_pass_node.get_name(), course_name,
                                      label=f"{prereq_result['proportion_taking_next']:.3f} ({prereq_result['number_taking_next']})"))

            students_who_did_take_next = prereq_result['students_who_did_take_next']
            combined_df = get_combined_course_df(df, students_who_did_take_next, students_in_alternate_entry)
            descriptives = analyze_course(course_name, combined_df, **filter_kwargs(include_node_pie=True))
            #print(descriptives)

            # Get the proportions for course demographics if node_pie == True
            if node_pie and descriptives:
                pie_data = descriptives.get("first_attempt_proportions")
                print(pie_data)
            else:
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


def make_pie_node(node_id, demographic_proportions):
    """
    Creates a pydot node with a pie wedge fill to represent demographic proportions.

    Parameters
    ----------
    node_id : str
        Unique identifier for the node.
    demographic_proportions : dict
        Mapping of color names to proportions (e.g., {'green': 0.6, 'blue': 0.4}).

    Returns
    -------
    pydot.Node
        A circle-shaped node styled with demographic wedges.

    Notes: DEPRECATED?
    """

    wedges = [f"{color};{proportion:.2f}" for color, proportion in demographic_proportions.items()]
    fillcolor = ":".join(wedges)

    print(f"Rendering pie node {node_id} with fillcolor: {fillcolor}")

    return pydot.Node(
        name=node_id,
        label=node_id,  # ← REQUIRED FOR RENDERING
        shape="circle",
        style="wedged",
        fillcolor=fillcolor,
    )



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
    ax.pie(values, colors=colors, wedgeprops=dict(edgecolor='white'))
    ax.axis('equal')  # Keep circular

    plt.savefig(filepath, transparent=True, bbox_inches='tight', pad_inches=0.15)
    plt.close()

def create_course_node_with_image(course_name, image_path):
    """
    Creates a box-shaped pydot node with an embedded pie chart image and a label.

    Parameters
    ----------
    course_name : str
        Label to display below the pie chart image.
    image_path : str
        Path to the PNG image to embed within the node.

    Returns
    -------
    pydot.Node
        A box-shaped node embedding an image and labeled with the course name.
    """

    return pydot.Node(
        name=course_name,
        label=f"\n\n{course_name}",
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