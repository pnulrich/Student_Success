# flagging.py
"""
Functions to assign categorical flags for student retention, inactivity, and graduation status.
These are low-level utilities designed for reuse across retention summaries, hazard modeling,
and visualization modules.
"""

import pandas as pd
import ast
from student_success.utils.constants import STEM_CORE_MAJORS

def assign_retention_outcomes(df, major_col='major_term', reference_col='major_term_earliest',
                              stem_majors=STEM_CORE_MAJORS, flag_stem=True):
    """
    Assigns binary flags for retention in major and (optionally) retention in STEM fields.

    Parameters:
        df (pd.DataFrame): Input dataframe.
        major_col (str): Column indicating student's current major.
        reference_col (str): Column indicating reference major (e.g., at matriculation).
        stem_majors (list): List of STEM major codes.
        flag_stem (bool): Whether to assign STEM retention flag.

    Returns:
        pd.DataFrame: Copy of input dataframe with 'flag_retention_major' and optionally 'flag_retention_STEM'.
                      Students who did not start in STEM are flagged with -1 in 'flag_retention_STEM'.
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

def classify_dropout_term(df, term_col='demographics_term', student_col='student_ID', student_level = 'US', graduation_flag_col='flag_graduation', threshold=3, graduation_target_level='B', graduation_level_col='graduation_level', status_col='graduation_status'):
    """
    Flags the last term of enrollment as the dropout point if the student has not graduated at the specified level and does not return for more than `threshold` terms.

    Parameters:
        df (pd.DataFrame): DataFrame with student-term records.
        term_col (str): Column indicating term of enrollment (e.g., 'demographics_term').
        student_col (str): Column identifying the student (e.g., 'student_ID').
        graduation_flag_col (str): Column with binary indicator of graduation (1 = graduated).
        threshold (int): Number of consecutive missing terms after last known enrollment to define dropout. Default is 3.
        target_level (str): Graduation level to assess inactivity against (default 'B').
        level_col (str): Column containing graduation levels.
        status_col (str): Column containing graduation statuses.

    Returns:
        pd.Series: Binary indicator per row where 1 = last active term before student dropped out, 0 = otherwise.
    """
    if graduation_flag_col not in df.columns:
        df['flag_graduation'] = classify_graduation_status(df, grad_col=status_col, grad_level=graduation_level_col, target_level=graduation_target_level)

    df = df.sort_values(by=[student_col, term_col])
    df['term_gap'] = 0
    df['dropout_flag'] = 0

    for student_id, group in df.groupby(student_col):
        if group[graduation_flag_col].max() == 1:
            continue  # skip graduated students

        terms = group[term_col].values
        deltas = []
        for i in range(1, len(terms)):
            gap = terms[i] - terms[i - 1]
            gap_years = gap // 100
            gap_sem = gap % 100
            term_gap = gap_years * 3 + (1 if gap_sem == 1 else 2 if gap_sem == 5 else 3 if gap_sem == 8 else 0)
            deltas.append(term_gap)
        deltas.append(0)  # No gap after last term

        if len(deltas) == 0:
            continue

        max_gap = max(deltas)
        if max_gap > threshold:
            max_idx = deltas.index(max_gap)
            row_indices = group.iloc[[max_idx]].index
            df.loc[row_indices, 'dropout_flag'] = 1

    return df['dropout_flag'].astype(int)




def classify_graduation_status(df, grad_col='graduation_status', level_col='graduation_level', target_level='B'):
    """
    Converts graduation status to binary indicator: 1 = graduated at the target level (e.g., Bachelor's), 0 = not.

    Parameters:
        df (pd.DataFrame): DataFrame with columns for graduation status and level.
        grad_col (str): Column containing a tuple (or stringified tuple) of award statuses.
        level_col (str): Column containing a tuple (or stringified tuple) of award levels (e.g., 'B', 'M').
        target_level (str): The graduation level to detect (e.g., 'B' for Bachelor's).

    Returns:
        pd.Series: Binary flag where 1 = graduated at the target level.
    """
    def interpret_and_check(row):
        try:
            statuses = row[grad_col]
            levels = row[level_col]

            if isinstance(statuses, str):
                statuses = statuses.strip("() ").split(",")
                statuses = [s.strip().strip("'") for s in statuses]
            if isinstance(levels, str):
                levels = levels.strip("() ").split(",")
                levels = [l.strip().strip("'") for l in levels]

            return int(any(
                status == 'Awarded' and level == target_level
                for status, level in zip(statuses, levels)
            ))
        except Exception:
            return 0

    return df.apply(interpret_and_check, axis=1).astype(int)


def classify_graduation_term(df, grad_date_col='graduation_date', level_col='graduation_level',
                             status_col='graduation_status', term_col='demographics_term', target_level='B', use_max_term_logic=True):
    """
    Identifies whether a student graduated at the specified level in the current term.

    Parameters:
        df (pd.DataFrame): DataFrame with one row per student per term.
        grad_date_col (str): Column containing a tuple (or stringified tuple) of graduation dates.
        level_col (str): Column containing a tuple (or stringified tuple) of degree levels.
        status_col (str): Column containing a tuple (or stringified tuple) of graduation statuses.
        term_col (str): Column with the current term (int, formatted as YYYYMM).
        target_level (str): The graduation level to detect (e.g., 'B' for Bachelor's).

    Returns:
        pd.Series: Binary flag where 1 indicates the student graduated at the target level in the current term.

    This function defaults to using max-term logic (use_max_term_logic=True), which:
        - Expects a column named 'max_course_term' per student.
        - Flags 1 if any graduation date for the target level is greater than or equal to the max enrolled term.
        - Avoids mismatches between term codes and actual graduation dates (e.g., May graduations vs Spring 2025).

    Notes:
        - If tuple lengths are inconsistent or data are malformed, zip operations may truncate.
        - If multiple graduation awards exist at the same degree level (e.g., two Bachelor's),
          this function will return 1 if any matching level/date/status trio aligns with the current term.
        - This could lead to misinterpretation in rare cases where different majors are earned in different terms.
        - This function explicitly handles mixed cases where graduation-level columns are native tuples or stringified tuples.
          See in-line comments for how ast.literal_eval is bypassed on native tuples to avoid exceptions.
        - Type mismatches caused by float NaNs or mixed-type tuples during aggregation are resolved by converting to strings.
    """
    def interpret_and_check(row):
        try:
            levels = row[level_col]
            dates = row[grad_date_col]
            statuses = row[status_col]

            if isinstance(levels, str):
                levels = levels.strip("() ").split(",")
                levels = [l.strip().strip("'") for l in levels]
            if isinstance(dates, str):
                dates = dates.strip("() ").split(",")
                dates = [d.strip().strip("'") for d in dates]
            if isinstance(statuses, str):
                statuses = statuses.strip("() ").split(",")
                statuses = [s.strip().strip("'") for s in statuses]

            awarded_indices = [i for i, lvl in enumerate(levels)
                               if lvl == target_level and i < len(statuses) and statuses[i] == 'Awarded']

            if not awarded_indices:
                return 0

            matching_dates = []
            for i in awarded_indices:
                if i < len(dates):
                    val = dates[i]
                    if not isinstance(val, str):
                        val = str(val)
                    val = val.strip()
                    if len(val) < 6 or val.lower() in {'nan', 'none', ''}:
                        continue
                    matching_dates.append(val)

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




# Placeholder for additional flagging logic to be ported from hazard_utils
# e.g., assign_dropout_flags, classify_retention_in_major
