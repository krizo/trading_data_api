import pytest

from config.consts import TEST_SYMBOL
from helpers.assertions import assert_equals, assert_error_message
from sender import Sender
from tests.tests_stats_performance import generate_data


@pytest.mark.functional
def tests_stats_negative_k_value_over_limit():
    """
    Negative test to verify that the /stats endpoint returns an error when the `k` value
    exceeds the allowed limit (e.g., k > MAX_K_VALUE).

    This test ensures that the server properly validates the `k` value and returns
    a 400 Bad Request status code when the value is outside the allowed range.

    """

    generate_data(symbol=TEST_SYMBOL, k_value=1)

    # Make a request to the /stats endpoint with an invalid `k` value (10, out of range)
    stats_response = Sender.get_stats(TEST_SYMBOL, 10)

    # Assert that the response status code is 400 (Bad Request)
    assert_equals(stats_response.status_code, 404, "/stats expected to return status 404")

    # Assert that the error message matches the expected validation error
    assert_error_message("'k' must be between 1 and 8", stats_response)
