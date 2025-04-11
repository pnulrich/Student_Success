import numpy as np

def shannon_entropy(probabilities, weights=None, normalize=True, base=2, tolerance=1e-6):
    """
    Calculate weighted or unweighted Shannon entropy.

    Parameters:
    - probabilities: List or array of probabilities (must sum to 1).
    - weights: List or array of weights (same length as probabilities). Defaults to None.
    - normalize: Whether to normalize weighted probabilities. Defaults to True.
    - base: Base of the logarithm (default is 2 for bits).
    - tolerance: Tolerance for checking if probabilities sum to 1 (default is 1e-6).

    Returns:
    - Weighted Shannon entropy (or unweighted if weights are None).
    """
    probabilities = np.array(probabilities, dtype=float)

    # Handle edge case: If all probabilities are 0, return entropy as 0
    if np.all(probabilities == 0):
        return 0.0

    # Normalize probabilities if they don't sum exactly to 1 (within tolerance)
    prob_sum = probabilities.sum()
    if not np.isclose(prob_sum, 1.0, atol=tolerance):
        raise ValueError(f"Probabilities must sum to 1 within tolerance {tolerance}. Got sum: {prob_sum}.")

    if weights is not None:
        weights = np.array(weights, dtype=float)
        # Calculate weighted probabilities
        weighted_probs = weights * probabilities
        # print("Weighted probabilities:", weighted_probs)

        if normalize:
            # Normalize weighted probabilities to sum to 1
            weighted_probs /= np.sum(weighted_probs)
            # print("Normalized weighted probabilities:", weighted_probs)

        # Calculate weighted entropy
        return -np.sum(weighted_probs * np.log(probabilities, where=(probabilities > 0)) / np.log(base))
    else:
        # Calculate standard Shannon entropy
        return -np.sum(probabilities * np.log(probabilities, where=(probabilities > 0)) / np.log(base))


def sum_weighted_proportions(probabilities, weights=None, tolerance=1e-6):

    probabilities = np.array(probabilities, dtype=float)

    # Handle edge case: If all probabilities are 0, return entropy as 0
    if np.all(probabilities == 0):
        return 0.0

    # Normalize probabilities if they don't sum exactly to 1 (within tolerance)
    prob_sum = probabilities.sum()
    if not np.isclose(prob_sum, 1.0, atol=tolerance):
        raise ValueError(f"Probabilities must sum to 1 within tolerance {tolerance}. Got sum: {prob_sum}.")

    if weights is not None:
        weights = np.array(weights, dtype=float)
        # Calculate weighted probabilities
        weighted_probs = weights * probabilities

        # Calculate weighted entropy
        return np.sum(weighted_probs)
    else:
        raise ValueError(f"Weights must be provided in order to calculate weighted sum of probabilities.")


