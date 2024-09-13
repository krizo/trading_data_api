import json
from typing import List, Iterable, Dict, Optional
import requests
import logging

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_COUNT
from helpers.decorators import log_execution_time
from helpers.generators import chunk_data
from main import LOG


class Sender:
    """
    A class that sends HTTP requests to the defined API endpoints.
    This class contains specific methods for each API operation.
    """
    base_url = "http://localhost:8000"

    @classmethod
    def send_request(cls, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> requests.Response:
        """
        Generic method for sending HTTP requests and logging information about them.

        :param method: HTTP method (GET, POST, DELETE).
        :param endpoint: API endpoint (without base URL).
        :param data: Payload for POST requests (optional).
        :param params: Query parameters for GET requests (optional).
        :return: Response object.
        """
        url = f"{cls.base_url}/{endpoint}"

        try:
            response = requests.request(method, url, json=data, params=params)
        except requests.RequestException as e:
            LOG.error(f"Request failed: {e}")
            raise

        return response

    @classmethod
    def add_batch(cls, symbol: str, values: List[float]) -> requests.Response:
        """
        Send a POST request to add a batch of trading prices for a given financial instrument.
        """
        endpoint = "add_batch"
        data = {"symbol": symbol, "values": values}
        return cls.send_request('POST', endpoint, data=data)

    @classmethod
    def get_values(cls, symbol: str) -> requests.Response:
        """
        Send a GET request to retrieve trading values for a specific symbol.
        """
        endpoint = f"get_values/{symbol}"
        return cls.send_request('GET', endpoint)

    @classmethod
    def delete_symbol(cls, symbol: str) -> requests.Response:
        """
        Send a DELETE request to remove a specific symbol from the database.
        """
        endpoint = f"delete_symbol/{symbol}"
        return cls.send_request('DELETE', endpoint)

    @classmethod
    def clear_db(cls) -> requests.Response:
        """
        Send a DELETE request to clear the entire database.
        """
        endpoint = "clear_db"
        return cls.send_request('DELETE', endpoint)

    @classmethod
    @log_execution_time
    def get_stats(cls, symbol: str, k: int) -> requests.Response:
        """
        Send a GET request to retrieve statistical analysis of trading data for a specific symbol.

        :param symbol: The financial instrument's identifier.
        :param k: An integer specifying the number of last 1e{k} data points to analyze.
        :return: The response from the API, which includes statistics (min, max, last, avg, var).
        """
        endpoint = "stats"
        params = {"symbol": symbol, "k": k}
        return cls.send_request('GET', endpoint, params=params)

    @classmethod
    def send_add_batch_data_in_chunks(cls, symbol: str, generated_data: Iterable[float],
                                      chunk_size: int = MAX_TRADE_POINTS_COUNT) -> List[float]:
        """
        Send trading values to the server in chunks and return the values sent.

        :param symbol: Financial instrument symbol.
        :param generated_data: Generator or iterable of trading values.
        :param chunk_size: Maximum size  of each chunk.
        :return: A list of all values sent to the server.
        """
        values_sent: List[float] = []

        # Convert generated_data to chunks
        chunks = chunk_data(generated_data, chunk_size)

        for chunk in chunks:
            add_response = cls.add_batch(symbol, chunk)
            if add_response.status_code != 200:
                LOG.error(f"Unexpected status code: {add_response.status_code}")
            values_sent.extend(chunk)
        return values_sent
