import json

from requests import Response

from main import LOG
import math


def assert_equals(actual_value: any, expected: any, description: str = None, tolerance: float = 1e-8):
    """
    Asserts that the actual value is approximately equal to the expected value, within a given tolerance.
    Raises an AssertionError if the values are not equal, including the provided description.

    :param actual_value: The actual value to check.
    :param expected: The expected value.
    :param description: A description of what is being checked (optional).
    :param tolerance: Tolerance for floating point comparisons (default is 1e-6).
    """

    if isinstance(actual_value, float) and isinstance(expected, float):
        # Apply tolerance for floating point comparisons
        if math.isclose(actual_value, expected, rel_tol=tolerance):
            return
        else:
            assert False, f"{description}: Expected value '{expected}', but got '{actual_value}'"

    if description:
        LOG.info(f"Checking {description}: expected {expected}, got {actual_value}.")

    assert actual_value == expected, (
        f"{description}: Expected value '{expected}', but got '{actual_value}'"
    )


def assert_error_message(expected_msg: str, response: Response):
    response_message = json.loads(response.content)
    error = response_message.get('detail')
    error_msg = error[0].get('msg').lower() if isinstance(error, list) else response_message.get('detail').lower()
    LOG.info(f"Check expected error message: {error_msg}")
    assert expected_msg in error_msg, f"Expected message {expected_msg} not in error message: {error_msg}"
