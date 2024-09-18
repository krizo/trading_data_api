import pytest
import numpy as np
from config.consts import MAX_K_VALUE, TEST_SYMBOL
from config.db import Database
from helpers.generators import generate_values, SymbolGenerator
from sender import Sender
from helpers.assertions import assert_equals, assert_error_message

k_values = range(1, MAX_K_VALUE + 1)


@pytest.fixture
def symbol() -> str:
    return TEST_SYMBOL


@pytest.fixture(autouse=True)
def database():
    """
    Clear database before all tests are ran
    """
    db = Database()
    db.clear()
    return db


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
    return {"symbol": symbol, "values": values_sent, "k": k}


@pytest.mark.parametrize("generate_data", k_values, indirect=True)
def tests_stats_positive_k_value_from_1_to_max(generate_data):
    values = generate_data["values"]
    k_value = generate_data["k"]

    db.add_batch

    stats_response = Sender.get_stats(TEST_SYMBOL, k_value)
    assert stats_response.ok, f"Request to stats failed with status {stats_response.status_code}"

    stats_data = stats_response.json()

    # Validate results against the truncated values
    assert_equals(actual_value=stats_data["min"], expected=np.min(values), description='stats["min"]')
    assert_equals(actual_value=stats_data["max"], expected=np.max(values), description='stats["min"]')
    assert_equals(actual_value=stats_data["last"], expected=values[-1], description='stats["last"]')
    assert_equals(actual_value=stats_data["avg"], expected=np.mean(values), description='stats["avg"]')
    assert_equals(actual_value=stats_data["var"], expected=np.var(values), description='stats["var"]')
    assert_equals(actual_value=stats_data["size"], expected=len(values), description='stats["size"]')


def tests_stats_negative_k_value_over_limit():
    """
    Negative test to check limit for k_value on /stats endpoint
    """
    symbol = 'TEST'
    stats_response = Sender.get_stats(symbol, 10)
    assert_equals(stats_response.status_code, 400, "/stats expected to be 400")
    assert_error_message("'k' must be between 1 and 8", stats_response)
