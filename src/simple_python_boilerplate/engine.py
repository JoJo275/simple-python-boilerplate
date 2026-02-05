"""
Core business logic and processing engine.

This module contains the core functionality of the application, independent of
any interface (CLI, API, etc.). It should be interface-agnostic and focused
purely on domain logic.

Typical contents:
    - Data processing functions
    - Business rule implementations
    - Core algorithms
    - State management

Usage:
    from simple_python_boilerplate.engine import process_data

Example:
    >>> from simple_python_boilerplate.engine import process_data
    >>> result = process_data(input_data)
"""


def process_data(data: str) -> str:
    """Process input data and return result.

    Args:
        data: Input data to process.

    Returns:
        Processed data string.
    """
    # Example implementation - replace with actual logic
    return f"Processed: {data}"


def validate_input(data: str) -> bool:
    """Validate input data before processing.

    Args:
        data: Input data to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not data:
        return False
    if not isinstance(data, str):
        return False
    return True
