from main import LOG


def assert_equals(actual_value: any, expected: any, description: str):
    """Asserts the two values are equal, or raises error including the provided description."""
    assert actual_value == expected, f"{description}, expected: '{expected}' != actual: '{actual}'"