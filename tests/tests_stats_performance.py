import numpy as np
import pytest

from config.consts import MAX_K_VALUE, TEST_SYMBOL
from helpers.assertions import assert_equals, assert_error_message
from helpers.generators import generate_values
from sender import Sender

# Parametry testowe dla wartości k od 1 do MAX_K_VALUE
k_values = range(1, MAX_K_VALUE + 1)


@pytest.fixture
def symbol() -> str:
    """
    Fixture that returns the test symbol for the financial instrument.

    Returns:
        str: The test symbol for the financial instrument.
    """
    return TEST_SYMBOL


@pytest.fixture(autouse=True)
def setup():
    """
    Fixture that clears the database before each test is executed.
    This ensures that each test starts with an empty database.
    """
    Sender.clear_db()


@pytest.fixture
def generate_data(request, symbol) -> dict:
    """
    Fixture that generates random trading data for a given `k` value.

    Args:
        request: The test request object containing the current parameter (`k` value).
        symbol: The financial instrument symbol for the data.

    Returns:
        dict: Dictionary containing the symbol, the generated trading values, and the `k` value.
    """
    k = request.param  # Retrieve the current k value from the test parameter
    num_values = 10 ** k  # Number of values to generate based on k

    # Generate random trading values
    values = generate_values(num_values)

    # Send the generated values to the server in chunks
    values_sent = Sender.send_add_batch_data_in_chunks(symbol=symbol, generated_data=values)

    return {"symbol": symbol, "values": values_sent, "k": k}


@pytest.mark.parametrize("generate_data", k_values, indirect=True)
def tests_stats_positive_k_value_from_1_to_max(generate_data):
    """
    Positive test to verify that the statistics endpoint (/stats) returns correct results
    for k values from 1 to MAX_K_VALUE.

    Args:
        generate_data: Fixture that provides the generated data and `k` value for the test.
    """
    values = generate_data["values"]
    k_value = generate_data["k"]

    # Make a request to the /stats endpoint for the test symbol and k_value
    stats_response = Sender.get_stats(TEST_SYMBOL, k_value)
    assert stats_response.ok, f"Request to stats failed with status {stats_response.status_code}"

    # Parse the response data
    stats_data = stats_response.json()

    # Validate each statistic against the expected values calculated from the generated data
    assert_equals(actual_value=stats_data["min"], expected=np.min(values), description='stats["min"]')
    assert_equals(actual_value=stats_data["max"], expected=np.max(values), description='stats["max"]')
    assert_equals(actual_value=stats_data["last"], expected=values[-1], description='stats["last"]')
    assert_equals(actual_value=stats_data["avg"], expected=np.mean(values), description='stats["avg"]')
    assert_equals(actual_value=stats_data["var"], expected=np.var(values), description='stats["var"]')
    assert_equals(actual_value=stats_data["size"], expected=len(values), description='stats["size"]')


def tests_stats_negative_k_value_over_limit(symbol):
    """
    Negative test to verify that the /stats endpoint returns an error when the `k` value
    exceeds the allowed limit (e.g., k > MAX_K_VALUE).

    This test ensures that the server properly validates the `k` value and returns
    a 400 Bad Request status code when the value is outside the allowed range.

    """

    # Make a request to the /stats endpoint with an invalid `k` value (10, out of range)
    stats_response = Sender.get_stats(symbol, 10)

    # Assert that the response status code is 400 (Bad Request)
    assert_equals(stats_response.status_code, 400, "/stats expected to return status 400")

    # Assert that the error message matches the expected validation error
    assert_error_message("'k' must be between 1 and 8", stats_response)
