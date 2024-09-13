import json

import pytest
import random
from typing import List, Dict
from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_COUNT
from helpers.generators import SymbolGenerator

from senders.sender import Sender

# Test data representing different negative scenarios
test_data_negative = [
    # {
    #     "symbol": "SYM11",  # Using a fixed symbol to check for uniqueness limit
    #     "values": [round(random.uniform(0.01, 1000.0), 2) for _ in range(MAX_TRADE_POINTS_COUNT)],
    #     "expected_status_code": 400,
    #     "expected_message": "symbol limit exceeded",
    #     "test_description": "Test with more than 10 unique symbols"
    # },
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
        "symbol": "THIS_IS_TOO_LONG",  # Invalid symbol length
        "values": [round(random.uniform(0.01, 1000.0), 2) for _ in range(MAX_TRADE_POINTS_COUNT)],
        "expected_status_code": 422,
        "expected_message": "string should have at most 10 characters",
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
    response_message = json.loads(response.content)
    error_msg = response_message.get('detail')[0].get('msg').lower()
    expected_msg = data.get('expected_message').lower()
    assert expected_msg in error_msg, f"Expected message '{data.get('expected_message')}' in error message: {error_msg}"


def test_add_batch_negative_too_many_symbols():
    ok_symbols = [f"SYM{i}" for i in range(MAX_SYMBOLS_COUNT)]
    for symbol in ok_symbols:
        response = Sender.add_batch(symbol=symbol, values=[100.0, 200.0, 300.0])
        assert response.ok
    response = Sender.add_batch(symbol="SYMX", values=[100.0, 200.0, 300.0])
    response_message = json.loads(response.content)
    expected_msg = f'symbols limit reached ({MAX_SYMBOLS_COUNT})'
    error_msg = response_message.get('detail').lower()
    assert expected_msg in error_msg, f"Expected message {expected_msg} not in error message: {error_msg}"
