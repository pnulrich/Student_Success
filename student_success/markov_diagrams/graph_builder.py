import pydot

### helper functions
def create_course_nodes(course_name, include_did_not_take_next=False, node_pie = False, pie_data = None):


    if node_pie and pie_data:
        print(f"Creating pie node for {course_name} with pie_data: {pie_data}")
        course_node = make_pie_node(course_name, pie_data)
    else:
        print(f"Creating default box node for {course_name}")
        course_node = pydot.Node(course_name, shape="box")

    # doing this avoids overwriting of the full dictionary and risk of silent replacement
    nodes = {}
    nodes["course"] = course_node
    nodes["pass"] = pydot.Node(f"Pass {course_name}", label="Pass")
    nodes["dfw"] = pydot.Node(f"DFW {course_name}", label="DFW")
    nodes["retake"] = pydot.Node(f"Retake {course_name}", label="Retake")

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
    # graph.add_node(node)
    # graph.add_edge(pydot.Edge(node, pydot.Node(course_name), label=f"{alt_entry_count}"))
    graph.add_edge(pydot.Edge(node, course_name, label=f"{alt_entry_count}"))

def get_combined_course_df(df, ids_1, ids_2):
    return df[df['student_ID'].isin(set(ids_1) | set(ids_2))]

# helper function that may be useful at some point...move to utils?
def get_earliest_major(df):
    df_sorted = df.sort_values(by=['student_ID', 'course_term'])
    earliest = df_sorted.groupby('student_ID').first()['major_term_earliest']
    df_merged = df.merge(earliest, how='left', on='student_ID', suffixes=('', '_Earliest'))
    df_merged['major_matriculation'] = df_merged['major_matriculation_Earliest'].fillna(df_merged['major_matriculation'])
    return df_merged.drop(columns=['major_matriculation_Earliest'])




def course_sequence_analysis(course_sequence, df, major_matriculation_column = 'major_term_earliest', target_major_code = None, node_pie=False):
    import pydot
    import matplotlib.pyplot as plt
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
            nodes = create_course_nodes(course_name, include_did_not_take_next=include_did_not_take,
                                        node_pie=node_pie, pie_data=pie_data)

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

            nodes = create_course_nodes(course_name, include_did_not_take_next=include_did_not_take,
                                        node_pie=node_pie, pie_data=pie_data)
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
    graph.write_png(image_filename)
    graph.write_raw("debug_graph.dot")

    fig = plt.figure(figsize=(10, 10))

    if target_major_code:
        fig.suptitle(f"Course Sequence Analysis for {target_major_code} Majors", fontsize=16)
    else:
        fig.suptitle(f"Course Sequence Analysis (no major filter applied)", fontsize=16)
    ax = fig.add_subplot(111)
    ax.axis('off')
    img = plt.imread(image_filename)
    ax.imshow(img)
    plt.show()


def make_pie_node(node_id, demographic_proportions):
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

