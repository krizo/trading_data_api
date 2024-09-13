import pytest
import numpy as np
from config.consts import MAX_K_VALUE
from config.db import Database
from helpers.generators import generate_values
from sender import Sender
from helpers.assertions import assert_equals

k_values = range(1, MAX_K_VALUE + 1)


@pytest.fixture(scope='session', autouse=True)
def symbol():
    return "AAPL"


pytest.fixture(scope='session', autouse=True)


def setup():
    """
    Clear database before all tests are ran
    """
    Sender.clear_db()


@pytest.fixture
def generate_data(request, symbol) -> dict:
    """
    Fixture that generates random trading data for a given `k` value.

    :param symbol: Test symbol for the financial instrument.
    :param request: Fixture request object containing the `k` value.
    :return: Dictionary with the symbol, chunks of generated values, and the `k` value.
    """
    k = request.param  # Retrieve the current k value from the param
    num_values = 10 ** k

    # Using a generator to create values
    values = generate_values(num_values)

    values_sent = Sender.send_add_batch_data_in_chunks(symbol=symbol, generated_data=values)

    # # Now we properly iterate over the chunks and send them
    # values_sent = Sender.send_add_batch_data_in_chunks(symbol, chunks)
    return {"symbol": symbol, "values": values_sent, "k": k}


@pytest.mark.parametrize("generate_data", k_values, indirect=True)
def tests_stats_positive_k_value_from_1_to_max(generate_data):
    values = generate_data["values"]
    symbol = generate_data["symbol"]
    k_value = generate_data["k"]

    stats_response = Sender.get_stats(symbol, k_value)
    assert stats_response.ok, f"Request to stats failed with status {stats_response.status_code}"

    stats_data = stats_response.json()

    # Calculate expected number of points
    num_points = min(10 ** k_value, len(values))

    # Extract last `num_points` from the values
    truncated_values = values[-num_points:]

    # Validate results against the truncated values
    assert_equals(actual_value=stats_data["min"], expected=np.min(truncated_values), description='stats["min"]')
    assert_equals(actual_value=stats_data["max"], expected=np.max(truncated_values), description='stats["min"]')
    assert_equals(actual_value=stats_data["last"], expected=truncated_values[-1], description='stats["last"]')
    assert_equals(actual_value=stats_data["avg"], expected=np.mean(truncated_values), description='stats["avg"]')
    assert_equals(actual_value=stats_data["var"], expected=np.var(truncated_values), description='stats["var"]')
    assert_equals(actual_value=stats_data["size"], expected=len(truncated_values), description='stats["size"]')
