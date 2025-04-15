import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------
# Retention Rate Summary (for error bar plots)
# ---------------------------------------------

def _summarize_retention(df, semester_col, retention_col):
    """
    Compute mean retention, standard error, and count by semester.
    """
    stats = df.groupby(semester_col)[retention_col].agg(['mean', 'std', 'count']).reset_index()
    stats['mean'] *= 100  # Convert to percent
    stats['std'] = (stats['std'] / np.sqrt(stats['count'])) * 100  # Standard error
    return stats


def _calculate_retention_stats(df, semester_col, flag_col):
    """
    Compute retention % and standard error by semester.
    """
    def calc(group):
        n = len(group)
        p = group[flag_col].mean()
        se = np.sqrt(p * (1 - p) / n) * 100
        return pd.Series({'retention': p * 100, 'std_dev': se, 'total_students': n})

    return df.groupby(semester_col).apply(calc).reset_index()


# ---------------------------------------------
# Cumulative Retention Summary
# ---------------------------------------------

def _summarize_cumulative_retention(df, semester_col, major_col, grad_col):
    """
    Compute cumulative retention, graduation, and attrition rates by semester.
    """
    grouped = df.groupby(semester_col)
    retention = grouped[major_col].mean().cumsum()
    graduation = grouped[grad_col].mean().cumsum()
    leaving = 1 - (retention + graduation)

    return pd.DataFrame({
        semester_col: retention.index,
        'retention': retention.values * 100,
        'graduation': graduation.values * 100,
        'leaving': leaving.values * 100
    })


# ---------------------------------------------
# Shared Visualization Utilities
# ---------------------------------------------

def _plot_retention_with_histogram(stats_df, semester_col, title, label, xlim_range=None):
    """
    Create a dual-axis plot: retention with error bars + student count histogram.
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.errorbar(
        stats_df[semester_col], stats_df['mean'], yerr=stats_df['std'],
        fmt='o-', capsize=5, label=label, color='tab:blue'
    )
    ax1.set_title(title)
    ax1.set_xlabel('Semester Number')
    ax1.set_ylabel('Retention Rate (%)', color='tab:blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.bar(stats_df[semester_col], stats_df['count'], alpha=0.3, color='grey', label='Total Students')
    ax2.set_ylabel('Number of Students', color='grey')
    ax2.tick_params(axis='y', labelcolor='grey')

    if xlim_range:
        ax1.set_xlim(xlim_range)
        ax2.set_xlim(xlim_range)

    fig.tight_layout()
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.show()


# ---------------------------------------------
# Public Plotting Functions
# ---------------------------------------------

def plot_retention_rate(
    cleaned_df,
    semester_col='semester_number',
    major_retention_col='flag_retention_major',
    stem_retention_col='flag_retention_STEM',
    stem_plot=True,
    major_plot=True,
    major_list=None,
    xlim_range=None
):
    """
    Plots the retention rate for a specified major and optionally for STEM majors.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
    semester_col : str
    major_retention_col : str
    stem_retention_col : str
    stem_plot : bool
    major_plot : bool
    major_list : list
    xlim_range : tuple

    Returns
    -------
    None
    """
    if major_list is None:
        major_list = []

    major_df = cleaned_df[cleaned_df['major_earliest_term'].isin(major_list)].copy()

    if major_plot:
        major_stats = _summarize_retention(major_df, semester_col, major_retention_col)
        _plot_retention_with_histogram(
            major_stats,
            semester_col=semester_col,
            title=f'Cumulative {major_list} Major Retention Rate',
            label='Major Retention Rate',
            xlim_range=xlim_range
        )

    if stem_plot:
        stem_stats = _summarize_retention(major_df, semester_col, stem_retention_col)
        _plot_retention_with_histogram(
            stem_stats,
            semester_col=semester_col,
            title='Cumulative STEM Major Retention Rate',
            label='STEM Retention Rate',
            xlim_range=xlim_range
        )


def plot_cumulative_retention_rate(
    cleaned_df,
    semester_col='semester_number',
    major_retention_col='flag_retention_major',
    stem_retention_col='flag_retention_STEM',
    grad_col='graduation_flag',
    stem_plot=True,
    major_plot=True,
    major_list=None
):
    """
    Plots cumulative retention, graduation, and attrition rates.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
    semester_col : str
    major_retention_col : str
    stem_retention_col : str
    grad_col : str
    stem_plot : bool
    major_plot : bool
    major_list : list

    Returns
    -------
    None
    """
    if major_list is None:
        major_list = []

    major_df = cleaned_df[cleaned_df['major_earliest_term'].isin(major_list)].copy()

    if major_plot:
        stats = _summarize_cumulative_retention(major_df, semester_col, major_retention_col, grad_col)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(stats[semester_col], stats['retention'], label='Major Retention', color='tab:blue')
        ax.plot(stats[semester_col], stats['graduation'], label='Graduation', color='tab:green')
        ax.plot(stats[semester_col], stats['leaving'], label='Attrition', color='tab:red')

        ax.set_title(f'Cumulative {major_list} Major Retention, Graduation, and Attrition')
        ax.set_xlabel('Semester Number')
        ax.set_ylabel('Cumulative Rate (%)')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()


def plot_major_retention_rate(
    cleaned_df,
    major='All',
    student_id_col='student_ID',
    major_col='major_matriculation',
    flag_col='flag_major_retention',
    semester_col='semester_number'
):
    """
    Retention rate plot for a specific major with error bars and student count.
    """
    if major != 'All':
        major_df = cleaned_df[cleaned_df[major_col] == major].copy()
    else:
        major_df = cleaned_df.copy()

    print(f'Unique students in {major}:', major_df[student_id_col].nunique(), f'(Records: {len(major_df)})')

    stats = _calculate_retention_stats(major_df, semester_col, flag_col)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.errorbar(stats[semester_col], stats['retention'], yerr=stats['std_dev'],
                 fmt='o-', capsize=5, label='Retention Rate', color='tab:blue')
    ax1.set_title(f'Cumulative {major} Major Retention Rate')
    ax1.set_xlabel('Semester Number')
    ax1.set_ylabel('Retention Rate (%)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.bar(stats[semester_col], stats['total_students'], alpha=0.3, color='grey', label='Total Students')
    ax2.set_ylabel('Number of Students', color='grey')
    ax2.tick_params(axis='y', labelcolor='grey')

    fig.tight_layout()
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.show()
