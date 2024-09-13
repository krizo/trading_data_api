from main import LOG


def assert_equals(actual_value: any, expected: any, description: str = None, round_precision: int = None):
    """Asserts the two values are equal, or raises error including the provided description."""
    if round_precision:
        actual_value, expected = round(actual_value, round_precision), round(expected, round_precision)
    if description:
        LOG.info(f"Check {description} value is {expected}.")
    assert actual_value == expected, f"{description}, expected: '{expected}' != actual: '{actual_value}'"
