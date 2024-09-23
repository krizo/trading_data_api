import json
import math
import random
import sys

import numpy as np
import pytest

from config.consts import MAX_TRADE_POINTS_COUNT
from helpers.assertions import assert_equals
from models.stats_response_model import StatsResponse
from sender import Sender

test_data = [
    {
        "symbol": "TST2",
        "values": list(range(1, 14))
    },
    {
        "symbol": "TST1",
        "values": [round(random.uniform(0.01, 1000.0), 2) for _ in range(MAX_TRADE_POINTS_COUNT)]
    },

    {
        "symbol": "TST3",
        "values": [0, 0.0]
    },
    {
        "symbol": "TST4",
        "values": [0, 0.0]
    },
    {
        "symbol": "TST5",
        "values": [math.sqrt(sys.float_info.max)]  # Can't be more because ** 2 is used in calculating variation
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


def test_add_batch_positive(data):
    """
    Test for adding a batch of trading data.
    Verifies if the batch request is successful.
    """
    response = Sender.add_batch(data.get('symbol'), data.get('values'))
    assert response.ok, f"Request failed for symbol: {data.get('symbol')}. Response: {response.text}"


@pytest.mark.functional
def test_get_stats_positive(data):
    """
    Test for getting statistics for trading values for a given symbol.
    """
    symbol, expected_values = data['symbol'], data['values']
    Sender.add_batch(symbol, expected_values)

    k_value = math.floor(math.log10(len(expected_values))) if len(expected_values) > 10 else 1
    response = Sender.get_stats(symbol, k_value)
    content = json.loads(response.content)

    # Check if all metrics are in the response
    assert sorted(StatsResponse.model_fields) == sorted(content.keys())

    n_last_values = data['values'][-10 ** k_value:]
    assert_equals(content['min'], np.min(n_last_values), "/stats/ 'min' value")
    assert_equals(content['max'], np.max(n_last_values), "/stats/ 'max' value")
    assert_equals(content['avg'], np.mean(n_last_values), "/stats/ 'avg' value")
    assert_equals(content['var'], np.var(n_last_values), "/stats/ 'var' value")
    assert_equals(content['last'], n_last_values[-1], "/stats/ 'last' value")
