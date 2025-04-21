import matplotlib.pyplot as plt
import pydot
from student_success.markov_diagrams.course_flows import (
    analyze_course,
    calculate_progression_to_next_course,
    calculate_alternate_entry
)


# 2023-10-28 (PNU, modified as extension from course_attempts_pydot() with ChatGPT4.0):
# uses data from combine_course_grades_with_demographics() to determine proportions of students who passed course
# course_sequence : list of strings representing names of courses of interest (e.g., "CALC FOR THE LIFE SCIENCES I")
# df : dataframe containing grades and demographics
# major_matriculation: string, code for major (e.g., "BIO")
# [not implemented yet] node_pie: boolean; optional parameter that can be used to demonstrate population stats (like % female) for a specific node
def course_sequence_analysis(course_sequence, df, major_matriculation, node_pie = False):
    """
     Analyze the progression of students through a sequence of courses.

     Parameters
     ----------
     course_sequence : list of str
         The sequence of courses to analyze.
     df : pandas DataFrame
         The DataFrame containing student enrollment data.
     major_matriculation : str
         The major matriculation of the students being considered.
     node_pie : bool, optional
         Whether to include pie charts in the node labels (default is False).

     Returns
     -------
     None
    """

    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    previous_pass_node = None

    df_sorted = df.sort_values(by=['student_ID', 'course_term'])
    earliest_major = df_sorted.groupby('student_ID').first()['major_matriculation']
    df_merged = df.merge(earliest_major, how='left', on='student_ID', suffixes=('', '_Earliest'))
    df_merged['major_matriculation'] = df_merged['major_matriculation_Earliest'].fillna(df_merged['major_matriculation'])
    df_merged.drop(columns=['major_matriculation_Earliest'], inplace=True)
    df = df_merged.copy()

    for index, course_name in enumerate(course_sequence):
        print(index)

        course_node = pydot.Node(course_name, shape="box")
        pass_node = pydot.Node(f"Pass {course_name}", label="Pass")
        dfw_node = pydot.Node(f"DFW {course_name}", label="DFW")
        retake_node = pydot.Node(f"Retake {course_name}", label="Retake")
        if index < len(course_sequence) - 1:
            did_not_take_next_node = pydot.Node(f"Did Not Take Next {course_name}", label="Did Not Take Next")

        graph.add_node(course_node)
        graph.add_node(pass_node)
        graph.add_node(dfw_node)
        graph.add_node(retake_node)
        if index < len(course_sequence) - 1:
            graph.add_node(did_not_take_next_node)

        if index == 0:
            descriptives = analyze_course(course_name, df, major_matriculation)
            proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, students_who_did_take_next = calculate_progression_to_next_course(
                current_course = course_name, next_course = course_sequence[index + 1], df = df, major_matriculation = major_matriculation)
            next_course_name = course_sequence[index + 1]
            print("Next course name : ", next_course_name)
            print("Number taking next : ", number_taking_next)
            graph.add_edge(pydot.Edge(pass_node, did_not_take_next_node,
                                      label=f"{proportion_not_taking_next:.3f} ({number_not_taking_next})"))

        if index > 0:
            prerequisite_course_name = course_sequence[index - 1]
            print("The prerequisite course name is ", prerequisite_course_name, "and current course is",
                  course_sequence[index])
            if index < (len(course_sequence) - 1):
                alternate_entry_results = calculate_alternate_entry(
                    current_course=course_name,
                    prior_course=prerequisite_course_name,
                    df=df,
                    major_matriculation=major_matriculation
                )
                number_alternate_entry = alternate_entry_results['n_without_prior_pass']
                students_in_alternate_entry = alternate_entry_results['alt_entry_ids']

                prerequisite_course_results = calculate_progression_to_next_course(
                    current_course = prerequisite_course_name, next_course = course_name, df = df, major_matriculation = major_matriculation)
                graph.add_edge(pydot.Edge(previous_pass_node, course_node,
                                          label=f"{prerequisite_course_results[2]:.3f} ({prerequisite_course_results[3]})"))

                current_course_df = df[(df['student_ID'].isin(students_who_did_take_next)) | (df['student_ID'].isin(students_in_alternate_entry))]
                print(course_name)
                descriptives = analyze_course(course_name, current_course_df, major_matriculation, course_sequence[index])

            if index == (len(course_sequence) - 1):
                prerequisite_course_name = course_sequence[index - 1]
                alternate_entry_results = calculate_alternate_entry(
                    current_course=course_name,
                    prior_course=prerequisite_course_name,
                    df=df,
                    major_matriculation=major_matriculation
                )
                number_alternate_entry = alternate_entry_results['n_without_prior_pass']
                students_in_alternate_entry = alternate_entry_results['alt_entry_ids']

                prerequisite_course_results = calculate_progression_to_next_course(
                    current_course=prerequisite_course_name, next_course=course_name, df=df,
                    major_matriculation=major_matriculation)

                graph.add_edge(pydot.Edge(previous_pass_node, course_node,
                                          label=f"{prerequisite_course_results[2]:.3f} ({prerequisite_course_results[3]})"))

                current_course_df = df[(df['student_ID'].isin(students_who_did_take_next)) | (
                    df['student_ID'].isin(students_in_alternate_entry))]
                print(course_name)
                descriptives = analyze_course(course_name, current_course_df, major_matriculation, course_sequence[index])

        print(descriptives)
        graph.add_edge(pydot.Edge(course_node, pass_node, label=f"{descriptives['first_pass_proportion']:.3f} ({descriptives['first_pass_number']})"))
        graph.add_edge(pydot.Edge(course_node, dfw_node, label=f"{descriptives['first_DFW_proportion']:.3f} ({descriptives['first_DFW_number']})"))
        graph.add_edge(pydot.Edge(dfw_node, retake_node, label=f"{descriptives['proportion_DFW_repeat']:.3f} ({descriptives['second_attempt_number']})"))
        if index < (len(course_sequence) - 1):
            graph.add_edge(pydot.Edge(dfw_node, did_not_take_next_node, label=f"{1-descriptives['proportion_DFW_repeat']:.3f} ({descriptives['first_DFW_number'] - descriptives['second_attempt_number']})"))
            graph.add_edge(pydot.Edge(retake_node, did_not_take_next_node, label=f"{descriptives['second_DFW_proportion']:.3f} ({descriptives['second_DFW_number']})"))
        graph.add_edge(pydot.Edge(retake_node, pass_node, label=f"{descriptives['second_pass_proportion']:.3f} ({descriptives['second_pass_number']})"))

        if (index > 0):
            if(index < (len(course_sequence) - 1)):
                next_course_name = course_sequence[index + 1]
                print("Course name : ", course_name)
                print("Next course name : ", next_course_name)
                proportion_not_taking_next, number_not_taking_next, proportion_taking_next, number_taking_next, students_who_did_take_next = calculate_progression_to_next_course(
                    course_name, next_course_name, df, major_matriculation)
                print("Number not taking next : ", number_not_taking_next)
                graph.add_edge(pydot.Edge(pass_node, did_not_take_next_node, label=f"{proportion_not_taking_next:.3f} ({number_not_taking_next})"))

            prerequisite_course_name = course_sequence[index -1]
            alternate_entry_results = calculate_alternate_entry(
                current_course=course_name,
                prior_course=prerequisite_course_name,
                df=df,
                major_matriculation=major_matriculation
            )
            number_alternate_entry = alternate_entry_results['n_without_prior_pass']
            students_in_alternate_entry = alternate_entry_results['alt_entry_ids']

            print(number_alternate_entry, len(students_in_alternate_entry))
            alternate_entry_node = pydot.Node(f"Alternate Entry to {course_name}", label="Alternate Entry")
            graph.add_node(alternate_entry_node)
            graph.add_edge(pydot.Edge(alternate_entry_node, course_node, label=f"{number_alternate_entry}"))

        previous_pass_node = pass_node

    graph.set("nodesep", "1.0")

    image_filename = "course_sequence_attempts_graph.png"
    graph.write_png(image_filename)

    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Course Sequence Analysis for {major_matriculation} Majors", fontsize=16)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()


### helper functions
def create_course_nodes(course_name, include_did_not_take_next=False):
    nodes = {
        "course": pydot.Node(course_name, shape="box"),
        "pass": pydot.Node(f"Pass {course_name}", label="Pass"),
        "dfw": pydot.Node(f"DFW {course_name}", label="DFW"),
        "retake": pydot.Node(f"Retake {course_name}", label="Retake")
    }
    if include_did_not_take_next:
        nodes["did_not_take_next"] = pydot.Node(f"Did Not Take Next {course_name}", label="Did Not Take Next")
    return nodes


def add_course_edges(graph, nodes, stats, include_did_not_take_next=False):
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
    node = pydot.Node(f"Alternate Entry to {course_name}", label="Alternate Entry")
    graph.add_node(node)
    graph.add_edge(pydot.Edge(node, pydot.Node(course_name), label=f"{alt_entry_count}"))

def get_combined_course_df(df, ids_1, ids_2):
    return df[df['student_ID'].isin(set(ids_1) | set(ids_2))]

def get_earliest_major(df):
    df_sorted = df.sort_values(by=['student_ID', 'course_term'])
    earliest = df_sorted.groupby('student_ID').first()['major_matriculation']
    df_merged = df.merge(earliest, how='left', on='student_ID', suffixes=('', '_Earliest'))
    df_merged['major_matriculation'] = df_merged['major_matriculation_Earliest'].fillna(df_merged['major_matriculation'])
    return df_merged.drop(columns=['major_matriculation_Earliest'])


def course_sequence_analysis_new(course_sequence, df, major_matriculation, node_pie=False):
    import pydot
    import matplotlib.pyplot as plt
    from student_success.markov_diagrams.course_flows import (
        analyze_course, calculate_alternate_entry, calculate_progression_to_next_course
    )

    graph = pydot.Dot(graph_type="digraph", strict=False, rankdir="TB")
    previous_pass_node = None
    df = get_earliest_major(df)

    for index, course_name in enumerate(course_sequence):
        print(index)

        is_last = index == len(course_sequence) - 1
        is_first = index == 0
        include_did_not_take = index < len(course_sequence) - 1

        # Create and add course nodes
        nodes = create_course_nodes(course_name, include_did_not_take_next=include_did_not_take)
        for node in nodes.values():
            graph.add_node(node)

        if is_first:
            descriptives = analyze_course(course_name, df, major_matriculation)

            progression = calculate_progression_to_next_course(course_name, course_sequence[index + 1], df, major_matriculation)

            print("Next course name : ", course_sequence[index + 1])
            print("Number taking next : ", progression['number_taking_next'])

            graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
                                      label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))

        else:
            prerequisite = course_sequence[index - 1]
            print("The prerequisite course name is", prerequisite, "and current course is", course_name)

            alt_entry = calculate_alternate_entry(course_name, prerequisite, df, major_matriculation)
            add_alternate_entry(graph, course_name, alt_entry['n_without_prior_pass'])
            students_in_alternate_entry = alt_entry['alt_entry_ids']

            prereq_result = calculate_progression_to_next_course(prerequisite, course_name, df, major_matriculation)
            graph.add_edge(pydot.Edge(previous_pass_node, nodes['course'],
                                      label=f"{prereq_result['proportion_taking_next']:.3f} ({prereq_result['number_taking_next']})"))

            students_who_did_take_next = prereq_result['students_who_did_take_next']
            combined_df = get_combined_course_df(df, students_who_did_take_next, students_in_alternate_entry)
            descriptives = analyze_course(course_name, combined_df, major_matriculation)

            if not is_last:
                next_course = course_sequence[index + 1]
                print("Course name : ", course_name)
                print("Next course name : ", next_course)

                progression = calculate_progression_to_next_course(course_name, next_course, df, major_matriculation)

                print("Number not taking next : ", progression['number_not_taking_next'])
                graph.add_edge(pydot.Edge(nodes['pass'], nodes['did_not_take_next'],
                                          label=f"{progression['proportion_not_taking_next']:.3f} ({progression['number_not_taking_next']})"))

        print(descriptives)
        add_course_edges(graph, nodes, descriptives, include_did_not_take_next=include_did_not_take)
        previous_pass_node = nodes['pass']

    graph.set("nodesep", "1.0")
    image_filename = "course_sequence_attempts_graph.png"
    graph.write_png(image_filename)

    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Course Sequence Analysis for {major_matriculation} Majors", fontsize=16)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()
