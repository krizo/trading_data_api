import json
import sys
import pytest

from helpers.assertions import assert_equals
from helpers.generators import SymbolGenerator
from senders.sender import Sender

# Test data
test_data = [
    {
        "symbol": next(SymbolGenerator()),
        "values": [123.45, 124.56, 125.67, 126.78]
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": [0, 0.0]
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": [sys.float_info.min, -sys.float_info.min]
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": [sys.float_info.max, -sys.float_info.max]
    },
]


@pytest.fixture(params=test_data, ids=lambda param: f"{param.get('symbol')}")
def data(request) -> dict:
    """
    Provides the test data for each test case.
    :param request: Pytest request object with param containing test data.
    :return: Test data for the current test iteration.
    """
    return request.param


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """
    Setup function to clear the database before each test.
    This fixture is automatically applied to each test function.
    """
    Sender.clear_db()  # Clear the DB before each test
    yield  # Run test
    # No teardown needed, but you can add cleanup code if necessary


def test_add_batch_positive(data):
    """
    Test for adding a batch of trading data.
    Verifies if the batch request is successful.
    """
    response = Sender.add_batch(data.get('symbol'), data.get('values'))
    assert response.ok, f"Request failed for symbol: {data.get('symbol')}"


def test_get_values_positive(data):
    """
    Test for retrieving trading values for a given symbol.
    Verifies if the returned data matches the expected values.
    """
    symbol, expected_values = data['symbol'], data['values']

    # Add batch first
    Sender.add_batch(symbol, expected_values)

    # Get the values
    response = Sender.get_values(symbol)
    assert response.ok, "Request failed"

    # Parse response content
    content = json.loads(response.content)

    # Validate the response content
    assert_equals(actual_value=content['symbol'], expected=symbol, description="Invalid symbol value")
    assert_equals(actual_value=content['values'], expected=expected_values, description="Invalid values")
