import numpy as np
import pytest

from config.consts import MAX_K_VALUE, TEST_SYMBOL
from helpers.assertions import assert_equals
from helpers.decorators import log_execution_time
from helpers.generators import generate_values
from main import LOG
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


@pytest.fixture(params=k_values, ids=lambda param: f"k={param}")
def k_value(request) -> int:
    return request.param


@log_execution_time
def generate_data(symbol: str, k_value: int) -> dict:
    """
    Fixture that generates random trading data for a given `k` value.

    Args:
        k_value: current parameter (`k` value) which will determine number of records.
        symbol: The financial instrument symbol for the data.

    Returns:
        dict: Dictionary containing the symbol, the generated trading values, and the `k` value.
    """
    num_values = 10 ** k_value  # Number of values to generate based on k

    LOG.info(f"Loading {num_values} values via /add_batch ")
    # Generate random trading values
    values = generate_values(num_values)
    LOG.info("Load done.")

    values_sent = Sender.send_add_batch_data_in_chunks(symbol=symbol, generated_data=values)

    return {"symbol": symbol, "values": values_sent, "k": k_value}


@pytest.mark.performance
def tests_stats_load_k_value_from_1_to_max(k_value):
    """
    Positive test to verify that the statistics endpoint (/stats) returns correct results
    for k values from 1 to MAX_K_VALUE.

    @param k_value: `k` value for the test (10^k records to be created)
    """
    data = generate_data(symbol=TEST_SYMBOL, k_value=k_value)
    values = data['values']

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

