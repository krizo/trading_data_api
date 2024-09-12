from typing import Dict, List

import numpy as np
from fastapi import HTTPException

from config.consts import MAX_SYMBOLS_COUNT, MAX_TRADE_POINTS_COUNT
from helpers.decorators import log_execution_time


class Database:
    """
    A simple in-memory database for storing and retrieving trading data for financial instruments.

    This class allows for adding, retrieving, and deleting financial instrument data, as well as performing
    statistical analysis on recent trading prices for specified symbols.
    """

    def __init__(self):
        self.data: Dict[str, List[float]] = {}

    def __name__(self):
        return "Server"

    def add_values(self, symbol: str, values: list):
        """
        Add a batch of trading prices for a given financial instrument.
        :param symbol: String identifier for the financial instrument.
        :param values: List of floating-point numbers representing trading prices to be added.
        """
        if symbol not in self.data:
            if len(self.data.keys()) == MAX_SYMBOLS_COUNT:
                HTTPException(status_code=404, detail=f"Symbols limit reached ({MAX_SYMBOLS_COUNT})")
            self.data[symbol] = []
        if len(values) > MAX_TRADE_POINTS_COUNT:
            HTTPException(status_code=404, detail=f"Values count is abpve the limit ({MAX_TRADE_POINTS_COUNT})")
        self.data[symbol].extend(values)

    def get_values(self, symbol: str, num_points: int = 10):
        """
        Retrieve the most recent `num_points` data points for the specified financial instrument.
        Raises an HTTPException if the symbol is not found or there is no data available.
        :param symbol: Financial instrument identifier.
        :param num_points: Number of data points to retrieve (default 10).
        :return: List of recent data points.
        """
        if symbol not in self.data:
            raise HTTPException(status_code=404, detail="Symbol not found")

        values = self.data[symbol][-num_points:]

        if not values:
            raise HTTPException(status_code=400, detail="No data points available for analysis")

        return values

    def delete_symbol(self, symbol: str):
        """
        Delete all trading data for a specified financial instrument.
        Raises an HTTPException if the symbol is not found in the database.
        :param symbol: Financial instrument identifier.
        """
        if symbol not in self.data:
            raise HTTPException(status_code=404, detail="Symbol not found")

        del self.data[symbol]

    def clear(self):
        """
        Clear the entire in-memory database of all data.
        """
        self.data.clear()

    @log_execution_time
    def calculate_stats(self, symbol: str, k: int):
        """
        Perform statistical analysis on the recent trading data for a specified financial instrument.

        This method computes the minimum, maximum, most recent, average, and variance of the last `1e{k}` data points.

        Raises an HTTPException if the symbol is not found or if `k` is out of the valid range (1-8).

        :param symbol: Financial instrument identifier.
        :param k: An integer from 1 to 8 specifying the number of last 1e{k} data points to analyze.
        :return: A dictionary containing the calculated statistical values (min, max, last, avg, var).
        """
        if k < 1 or k > 8:
            raise HTTPException(status_code=400, detail="Parameter 'k' must be between 1 and 8")

        num_points = int(10 ** k)
        values = self.get_values(symbol, num_points)

        if not values:
            raise HTTPException(status_code=404, detail="No data found for the given symbol")

        # Initialize variables for calculating stats
        min_value = float('inf')
        max_value = float('-inf')
        sum_value = 0
        sum_square = 0
        n = len(values)

        # One-pass calculation for min, max, sum, and sum of squares
        for value in values:
            min_value = min(min_value, value)
            max_value = max(max_value, value)
            sum_value += value
            sum_square += value ** 2

        avg_value = sum_value / n
        variance = (sum_square / n) - (avg_value ** 2)

        # Return the computed stats
        stats = {
            "min": min_value,
            "max": max_value,
            "last": values[-1],
            "avg": avg_value,
            "var": variance,
        }

        return stats

        # Numpy (k=8 -> 2 min 38 sec)
        # stats = {
        #     "min": np.min(values),
        #     "max": np.max(values),
        #     "last": values[-1],
        #     "avg": np.mean(values),
        #     "var": np.var(values),
        # }
        # return stats
