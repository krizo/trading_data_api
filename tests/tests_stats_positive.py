import json
from typing import Dict, List

import pytest
import random
import numpy as np

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_K_VALUE
from helpers.tools import chunk_data
from main import LOG
from senders.sender import Sender
from helpers.assertions import assert_equals

k_values = range(1, MAX_K_VALUE + 1)


# @pytest.fixture(scope='session', autouse=True)
# def symbol():
#     return "AAPL"


@pytest.fixture(scope="session")
def generate_data(request):
    """
    Generate trading data for a given symbol and split it into chunks.


    This fixture generates a specified number of random trading values based on the provided `k_value`,
    which determines the number of points to generate as 10^MAX_K_VALUE. The generated data is divided into
    chunks with a maximum size defined by `MAX_TRADE_POINTS_COUNT`.

    It's used to feed the "background" data. The real data to check calculations are being injected by
    generate_data fixture.

    The fixture is automatically executed for every test due to `autouse=True`.

    :return: A dictionary containing:
        - "symbol": Test symbol for the financial instrument.
        - "chunks": A list of lists, where each sublist contains a chunk of generated trading values.
        - "k": The `k_value` used to generate the data.
    """
    symbol = 'AAPL'
    num_values = 10 ** MAX_K_VALUE + 1000000
    # num_values = 1000000
    values = [round(random.uniform(0.01, 1000.0), 2) for _ in range(num_values)]

    chunks = list(chunk_data(values, MAX_TRADE_POINTS_COUNT))
    values_sent = send_add_values_in_chunks(symbol=symbol, chunks=chunks)
    LOG.info(
        f"SETUP: Added {len(values_sent)} values in {len(chunks)} chunk{'s' if len(chunks) > 1 else ''} for {symbol}")
    return {"symbol": symbol, "values": values_sent}


def send_add_values_in_chunks(symbol: str, chunks: List[List[float]]) -> [float]:
    values_sent: List[float] = []
    for values in list(chunks):
        add_response = Sender.add_batch(symbol, values)
        assert add_response.status_code == 200, f"Unexpected status code: {add_response.status_code}"
        values_sent.extend(values)
    return values_sent


@pytest.mark.parametrize("k_value", k_values)
def tests_stats_positive_k_value_from_1_to_max(generate_data, k_value):
    all_values = generate_data["values"]
    symbol = generate_data["symbol"]

    # Calculate expected number of points
    num_points = min(10 ** k_value, len(all_values))  # Ensure we don't exceed available points

    # Extract last `num_points` from the values - these will be data to tests
    stat_data = all_values[-num_points:]

    # values = send_add_values_in_chunks(symbol, chunks)

    # LOG.info(f"Added {len(values)} values in {len(chunks)} chunk{'s' if len(chunks) > 1 else ''} for {symbol}")

    stats_response = Sender.get_stats(symbol, k_value)
    assert stats_response.ok, f"Request to stats failed with status {stats_response.status_code}"

    stats_data = stats_response.json()

    # Validate results against the truncated values
    assert_equals(actual_value=stats_data["min"], expected=np.min(stat_data),
                  description="Invalid min value in stats")
    assert_equals(actual_value=stats_data["max"], expected=np.max(stat_data),
                  description="Invalid max value in stats")
    assert_equals(actual_value=stats_data["last"], expected=stat_data[-1],
                  description="Invalid last value in stats")
    assert_equals(actual_value=round(stats_data["avg"], 4), expected=round(np.mean(stat_data), 4),
                  description="Invalid avg value in stats")
    assert_equals(actual_value=round(stats_data["var"], 2), expected=round(np.var(stat_data), 2),
                  description="Invalid var value in stats")
