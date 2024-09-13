import pytest
import random
from typing import Dict

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_COUNT, MAX_SYMBOLS_LENGTH
from helpers.assertions import assert_error_message
from helpers.generators import SymbolGenerator

from sender import Sender

# Test data representing different negative scenarios
test_data_negative = [
    {
        "symbol": next(SymbolGenerator()),
        "values": [round(random.uniform(0.01, 1000.0), 2) for _ in range(MAX_TRADE_POINTS_COUNT + 1)],
        # More than 10,000 values
        "expected_status_code": 422,
        "expected_message": f"list should have at most 10000 items after validation, not {MAX_TRADE_POINTS_COUNT + 1}",
        "test_description": "Test where the array size exceeds 10,000 values"
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": [],  # Empty array
        "expected_status_code": 422,
        "expected_message": "list should have at least 1 item after validation",
        "test_description": "Test with an empty data array"
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": ["invalid", "data", 1.0],  # Invalid data format
        "expected_status_code": 422,
        "expected_message": "input should be a valid number, unable to parse string as a number",
        "test_description": "Test with invalid data format (strings instead of floats)"
    },
    {
        "symbol": next(SymbolGenerator()),
        "values": [round(random.uniform(-1000.0, -0.01), 2) for _ in range(10)],  # Negative values
        "expected_status_code": 422,
        "expected_message": "All values must be greater than 0.",
        "test_description": "Test with out-of-range values (negative values)"
    },
    {
        "symbol": next(SymbolGenerator(length=MAX_SYMBOLS_LENGTH + 1)),
        "values": [round(random.uniform(0.01, 1000.0), 2) for _ in range(MAX_TRADE_POINTS_COUNT)],
        "expected_status_code": 422,
        "expected_message": f'Symbol length must not exceed {MAX_SYMBOLS_LENGTH} characters.',
        "test_description": "Test with symbol exceeding the maximum length"
    }
]


@pytest.fixture(params=test_data_negative, ids=lambda param: f"{param.get('test_description')}")
def data(request) -> Dict:
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


def test_add_batch_negative(data):
    """
    Test for adding a batch of trading data with negative cases.
    Verifies if the batch request fails as expected.

    :param data: Test data for the current iteration.
    """
    response = Sender.add_batch(data.get('symbol'), data.get('values'))
    assert response.status_code == data.get('expected_status_code'), \
        f"Unexpected status code for symbol: {data.get('symbol')}. Response: {response.text}"
    expected_msg = data.get('expected_message').lower()
    assert_error_message(expected_msg=expected_msg, response=response)


def test_add_batch_negative_too_many_symbols():
    ok_symbols = [f"SYM{i}" for i in range(MAX_SYMBOLS_COUNT)]
    for symbol in ok_symbols:
        response = Sender.add_batch(symbol=symbol, values=[100.0, 200.0, 300.0])
        assert response.ok
    response = Sender.add_batch(symbol="SYMX", values=[100.0, 200.0, 300.0])
    expected_msg = f'symbols limit reached ({MAX_SYMBOLS_COUNT})'
    assert_error_message(expected_msg=expected_msg, response=response)


