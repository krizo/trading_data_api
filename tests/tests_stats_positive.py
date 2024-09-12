import json
from typing import Dict, List

import pytest
import random
import numpy as np

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_K_VALUE
from helpers.generators import SymbolGenerator
from helpers.tools import chunk_data
from main import LOG
from senders.sender import Sender
from helpers.assertions import assert_equals


@pytest.fixture
def generate_data(request) -> dict:
    """
    Fixture that generates random trading data for a given `k` value.

    :param request: Fixture request object containing the `k` value.
    :return: Dictionary with the symbol, chunks of generated values, and the `k` value.
    """
    k = request.param  # Retrieve the current k value from the param
    symbol = next(SymbolGenerator())
    num_values = 10 ** k

    values = [round(random.uniform(0.01, 1000.0), 2) for _ in range(num_values)]

    chunks = list(chunk_data(values, MAX_TRADE_POINTS_COUNT))
    return {"symbol": symbol, "chunks": chunks, "k": k}


k_values = range(1, MAX_K_VALUE + 1)


@pytest.mark.parametrize("generate_data", k_values, indirect=True)
def tests_stats_positive_k_value_from_1_to_max(generate_data):
    symbol = generate_data["symbol"]
    chunks = generate_data["chunks"]
    k_value = generate_data["k"]

    all_values: List[float] = []
    for values in list(chunks):
        add_response = Sender.add_batch(symbol, values)
        assert add_response.status_code == 200, f"Unexpected status code: {add_response.status_code}"
        all_values.extend(values)

    LOG.info(f"Added {len(all_values)} values in {len(chunks)} chunk{'s' if len(chunks) > 1 else ''} for {symbol}")
    stats_response = Sender.get_stats(symbol, k_value)
    assert stats_response.ok, f"Request to stats failed with status {stats_response.status_code}"

    stats_data = stats_response.json()

    # Calculate expected number of points
    num_points = min(10 ** k_value, len(all_values))  # Ensure we don't exceed available points

    # Extract last `num_points` from the values
    truncated_values = all_values[-num_points:]

    # Validate results against the truncated values
    assert_equals(actual_value=stats_data["min"], expected=np.min(truncated_values),
                  description="Invalid min value in stats")
    assert_equals(actual_value=stats_data["max"], expected=np.max(truncated_values),
                  description="Invalid max value in stats")
    assert_equals(actual_value=stats_data["last"], expected=truncated_values[-1],
                  description="Invalid last value in stats")
    assert_equals(actual_value=round(stats_data["avg"], 2), expected=round(np.mean(truncated_values), 2),
                  description="Invalid avg value in stats")
    assert_equals(actual_value=round(stats_data["var"], 2), expected=round(np.var(truncated_values), 2),
                  description="Invalid var value in stats")
