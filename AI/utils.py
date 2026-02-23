"""
utils.py
--------
Shared helper utilities.
Contains normalization, safe math, and reusable numeric helpers.
No business logic here.
"""


def safe_divide(numerator: float, denominator: float) -> float:
    """
    Prevents division by zero.
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """
    Restricts value within [min_value, max_value].
    """
    return max(min_value, min(value, max_value))


def normalize_ratio(value: float, max_reference: float) -> float:
    """
    Normalizes value against a reference max.
    """
    return clamp(safe_divide(value, max_reference))


def inverse_ratio(value: float, max_reference: float) -> float:
    """
    Computes inverse alignment:
    1 - (value / max_reference)
    """
    ratio = safe_divide(value, max_reference)
    return clamp(1 - ratio)


def compute_macro_density(protein: float, calories: float) -> float:
    """
    Computes protein efficiency per calorie.
    Assumes 0.3 as strong upper bound density.
    """
    density = safe_divide(protein, calories)
    return clamp(safe_divide(density, 0.3))


def percentage(part: float, whole: float) -> float:
    """
    Computes percentage safely.
    """
    return safe_divide(part, whole) * 100