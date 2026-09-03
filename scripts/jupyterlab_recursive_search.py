import os
import nbformat


def search_notebooks(root_dir, search_term, cell_type='code', ignore_case=True):
    """
    Recursively searches Jupyter notebooks for a specified term in selected cell types.

    Args:
        root_dir (str): Directory to search within.
        search_term (str): The term to search for.
        cell_type (str): 'code', 'markdown', or 'both' (default is 'code').
        ignore_case (bool): If True, search is case-insensitive (default True).

    Returns:
        List[dict]: A list of match dictionaries containing:
            - 'notebook': File path
            - 'cell_index': Index of the cell
            - 'matching_code': The matched source (code or markdown)
    """
    if cell_type not in ['code', 'markdown', 'both']:
        raise ValueError("cell_type must be one of 'code', 'markdown', or 'both'")

    results = []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".ipynb"):
                notebook_path = os.path.join(dirpath, filename)

                try:
                    with open(notebook_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)

                    for i, cell in enumerate(nb.cells):
                        if (
                            cell_type == 'both'
                            or cell.cell_type == cell_type
                        ):
                            source = cell.source
                            if ignore_case:
                                match = search_term.lower() in source.lower()
                            else:
                                match = search_term in source

                            if match:
                                results.append({
                                    "notebook": notebook_path,
                                    "cell_index": i,
                                    "matching_code": source.strip()
                                })

                except Exception as e:
                    print(f"Error processing {notebook_path}: {e}")

    return results


def concise_display(results):
    """
    Prints a concise summary of search results grouped by notebook file path.

    Args:
        results (List[dict]): The list of result dictionaries returned by `search_notebooks()`.
    """
    if results:
        match_paths = list(set(result['notebook'] for result in results))  # set → list for uniqueness
        for match_path in match_paths:
            print(f"Matching cells in {match_path}:")
            for result in results:
                if result['notebook'] == match_path:  # filter to this file
                    print(f"  Cell {result['cell_index']}")
                    # print(f"    {match['matching_code']}")  # Uncomment if you want to show code
            print("-" * 80)
    else:
        print("No matches found.")
