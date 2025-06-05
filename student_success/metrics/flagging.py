# flagging.py
"""
Functions to assign categorical flags for student retention, inactivity, and graduation status.
These are low-level utilities designed for reuse across retention summaries, hazard modeling,
and visualization modules.
"""

import pandas as pd
from student_success.utils.constants import STEM_CORE_MAJORS
from student_success.utils.validation import safe_parse_tuple

def assign_retention_outcomes(df, major_col='major_term', reference_col='major_term_earliest',
                              stem_majors=STEM_CORE_MAJORS, flag_stem=True):
    """
    Assigns binary flags for major retention and (optionally) STEM field retention.

    Parameters:
        df (pd.DataFrame): Input DataFrame with student major history.
        major_col (str): Column indicating current or observed major.
        reference_col (str): Column indicating original or reference major (e.g., major at matriculation).
        stem_majors (list): List of STEM major codes used to flag STEM retention (default = STEM_CORE_MAJORS).
        flag_stem (bool): Whether to assign a STEM retention flag.

    Returns:
        pd.DataFrame: A copy of the original DataFrame with two new columns:
            - 'flag_retention_major': 1 if current major matches reference major, else 0.
            - 'flag_retention_STEM':
                - 1 if student began in a STEM major and is still in STEM,
                - 0 if student left STEM,
                - -1 if student did not start in STEM.

    Notes:
        - Intended for use in longitudinal student tracking, retention summaries, and visualizations.
        - Major codes should be standardized and matched to the `stem_majors` list.
    """
    df = df.copy()
    df['flag_retention_major'] = (df[major_col] == df[reference_col]).astype(int)

    if flag_stem:
        # initialize values with a -1 for all students; thus, default is that students didn't start in STEM
        df['flag_retention_STEM'] = -1

        # for students who started in a core STEM major during their first term, set retention flag
        mask = df[reference_col].isin(stem_majors)
        df.loc[mask, 'flag_retention_STEM'] =(
            df.loc[mask,major_col].isin(stem_majors)
        ).astype(int)
    return df

def classify_dropout_term(df, term_col='demographics_term', student_col='student_ID', student_level_col='student_level',
                             graduation_flag_col='flag_graduation', threshold=3,
                             program_target_level='US', graduation_target_level='B',
                             graduation_level_col='graduation_level', graduation_status_col='graduation_status'):
    """
    Flags the final term of a student's enrollment as a dropout point under the following conditions:
    - The student has not graduated at the specified level, AND
    - EITHER they do not re-enroll for more than `threshold` terms,
      OR they transition from the target student level (e.g., bachelor's 'US') to a lower level (e.g., associate 'AS').

    Parameters:
        df (pd.DataFrame): DataFrame with one row per student per term.
        term_col (str): Column indicating the academic term (e.g., 'demographics_term'), formatted as YYYYMM.
        student_col (str): Column identifying the student (e.g., 'student_ID').
        student_level_col (str): Column indicating student level (e.g., 'US', 'AS').
        graduation_flag_col (str): Column with binary graduation flag (1 = graduated).
        threshold (int): Minimum number of terms without enrollment that defines a dropout (default = 3).
        program_target_level (str): Student level used to assess dropout (default = 'US' for bachelor's level).
        graduation_target_level (str): Graduation level required to override dropout logic (default = 'B').
        graduation_level_col (str): Column with graduation level(s), tuple or stringified tuple.
        graduation_status_col (str): Column with graduation status(es), tuple or stringified tuple.

    Returns:
        pd.Series: Binary indicator (1 = term where dropout occurred, 0 = otherwise).

    Notes:
        - Students who have graduated at the target level are not considered for dropout.
        - Dropout is applied to the term preceding a level change or final term if no subsequent activity is found.
        - Handles malformed tuples and stringified data gracefully.
    """
    if graduation_flag_col not in df.columns:
        df['flag_graduation'] = classify_graduation_status(
            df,
            grad_col=graduation_status_col,
            level_col=graduation_level_col,
            target_level=graduation_target_level
        )

    df = df.sort_values(by=[student_col, term_col])
    df['term_gap'] = 0
    df['flag_dropout_term'] = 0
    max_term_overall = df[term_col].max()

    for student_id, group in df.groupby(student_col):
        if group[graduation_flag_col].max() == 1:
            continue  # skip graduated students

        group = group.sort_values(by=term_col)
        terms = group[term_col].values
        levels = group[student_level_col].values

        deltas = []
        for i in range(1, len(terms)):
            gap = terms[i] - terms[i - 1]
            gap_years = gap // 100
            gap_sem = gap % 100
            term_gap = gap_years * 3 + (1 if gap_sem == 1 else 2 if gap_sem == 5 else 3 if gap_sem == 8 else 0)
            deltas.append(term_gap)

        deltas.append(0)  # No gap after last term

        for i in range(len(levels) - 1):
            if levels[i] == program_target_level and levels[i + 1] != program_target_level:
                df.loc[group.iloc[[i]].index, 'flag_dropout_term'] = 1
                break

        if group[student_col].iloc[-1] in df[df['flag_dropout_term'] == 1][student_col].values:
            continue  # already flagged by level transition

        if max(deltas) >= threshold:
            max_idx = deltas.index(max(deltas))
            df.loc[group.iloc[[max_idx]].index, 'flag_dropout_term'] = 1
        else:
            last_term = terms[-1]
            gap = max_term_overall - last_term
            gap_years = gap // 100
            gap_sem = gap % 100
            future_gap = gap_years * 3 + (1 if gap_sem == 1 else 2 if gap_sem == 5 else 3 if gap_sem == 8 else 0)
            if future_gap >= threshold:
                df.loc[group.index[-1], 'flag_dropout_term'] = 1

    return df['flag_dropout_term'].astype(int)



def classify_graduation_status(df, grad_col='graduation_status', level_col='graduation_level', target_level='B'):
    """
    Determines whether a student graduated at the target degree level based on award status and level.

    Parameters:
        df (pd.DataFrame): DataFrame with columns for graduation level and status.
        grad_col (str): Column containing tuple (or stringified tuple) of graduation statuses.
        level_col (str): Column containing tuple (or stringified tuple) of degree levels (e.g., 'B', 'M').
        target_level (str): Degree level to check for (default = 'B' for bachelor's).

    Returns:
        pd.Series: Binary indicator (1 = graduation at target level occurred, 0 = otherwise).

    Notes:
        - Mixed tuple/string data is normalized.
        - Students are flagged if any tuple pair (level, status) matches (target_level, 'Awarded').
        - Handles edge cases with truncated tuples or malformed strings gracefully.
    """

    def interpret_and_check(row):
        try:
            statuses = row[grad_col]
            levels = row[level_col]

            statuses = safe_parse_tuple(statuses)
            levels = safe_parse_tuple(levels)

            if len(statuses) != len(levels):
                print(f"[WARN] Tuple length mismatch: {row['student_ID']}")

            return int(any(
                status == 'Awarded' and level == target_level
                for status, level in zip(statuses, levels)
            ))
        except Exception:
            return 0

    return df.apply(interpret_and_check, axis=1).astype(int)


def classify_graduation_term(df, grad_date_col='graduation_date', level_col='graduation_level',
                             status_col='graduation_status', term_col='demographics_term', target_level='B',
                             use_max_term_logic=True):
    """
    Determines if a student graduated at the target level in the current term.

    Parameters:
        df (pd.DataFrame): DataFrame with one row per student per term.
        grad_date_col (str): Column containing a tuple (or stringified tuple) of graduation dates.
        level_col (str): Column containing a tuple (or stringified tuple) of graduation levels.
        status_col (str): Column containing a tuple (or stringified tuple) of graduation statuses.
        term_col (str): Column indicating the current term (e.g., 'demographics_term') in YYYYMM format.
        target_level (str): Degree level to evaluate (default = 'B' for bachelor's).
        use_max_term_logic (bool): If True, aligns graduation with max enrolled term instead of comparing by date.

    Returns:
        pd.Series: Binary flag (1 = student graduated at target level in this term, 0 = otherwise).

    Notes:
        - If `use_max_term_logic` is True:
            - Assumes a 'max_course_term' column exists.
            - A graduation is flagged if any awarded date for the target level is ≥ that max term.
        - If False:
            - Compares parsed graduation dates directly to the term's datetime.
        - Designed to handle malformed tuples and string representations robustly.
    """
    def interpret_and_check(row):

        try:
            levels = safe_parse_tuple(row[level_col])
            dates = safe_parse_tuple(row[grad_date_col])
            statuses = safe_parse_tuple(row[status_col])

            awarded_indices = [i for i, lvl in enumerate(levels)
                               if lvl == target_level and i < len(statuses) and statuses[i] == 'Awarded']

            if not awarded_indices:
                return 0

            matching_dates = [dates[i] for i in awarded_indices if i < len(dates)]
            parsed_dates = pd.to_datetime(matching_dates, errors='coerce')

            if use_max_term_logic:
                if 'max_course_term' not in row or pd.isna(row['max_course_term']):
                    return 0
                max_term = int(row['max_course_term'])
                term_date = pd.to_datetime(str(max_term), format='%Y%m', errors='coerce')

                return int(row[term_col] == max_term and any(pd.notna(d) and d >= term_date for d in parsed_dates))
            else:
                term_date = pd.to_datetime(str(row[term_col]), format='%Y%m', errors='coerce')

                return int(any(pd.notna(d) and d == term_date for d in parsed_dates))

        except Exception as e:
            print(f"[DEBUG] Exception for {row['student_ID']}: {e}")
            print("Row data:\n", row)
            return 0

    return df.apply(interpret_and_check, axis=1).astype(int)


def classify_graduation_in_major(df, major_col='major_graduation', target_major='BIO'):
    """
    Flags students whose graduation was in the specified target major.

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'major_graduation' column with final awarded majors.
        major_col (str): Column indicating graduation majors (e.g., a tuple of majors).
        target_major (str): Major of interest.

    Returns:
        pd.Series: Binary flag where 1 = graduated in target major, 0 = otherwise.
    """
    def flag_graduated_in_target(row):
        majors = safe_parse_tuple(row[major_col])
        return int(target_major in majors)

    return df.apply(flag_graduated_in_target, axis=1).astype(int)

def classify_graduation_in_first_major(df, major_col='major_graduation', reference_col='major_term_earliest'):
    """
    Flags students whose graduation includes their originally declared major.

    Parameters:
        df (pd.DataFrame): DataFrame with 'major_graduation' and 'major_term_earliest' columns.
        major_col (str): Column containing graduation majors (stringified or real tuples/lists).
        reference_col (str): Column with the student's original major (e.g., at matriculation).

    Returns:
        pd.Series: Binary flag (1 = graduated in first major, 0 = otherwise)
    """
    def flag_graduated_in_first_major(row):
        graduation_majors = safe_parse_tuple(row[major_col])
        return int(row[reference_col] in graduation_majors)

    return df.apply(flag_graduated_in_first_major, axis=1).astype(int)


def classify_graduation_in_STEM(df, major_col='major_graduation'):
    """
    Flags students whose graduation was in a core STEM major.

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'major_graduation' column with final awarded majors.
        major_col (str): Column indicating graduation majors (e.g., a tuple of majors).

    Returns:
        pd.Series: Binary flag where 1 = graduated in a core STEM major, 0 = otherwise.
    """
    def flag_graduated_in_STEM(row):
        graduation_majors = safe_parse_tuple(row[major_col])
        return int(any(m in STEM_CORE_MAJORS for m in graduation_majors))
    return df.apply(flag_graduated_in_STEM, axis=1).astype(int)


# Placeholder for additional flagging logic to be ported from hazard_utils
# e.g., assign_dropout_flags, classify_retention_in_major
