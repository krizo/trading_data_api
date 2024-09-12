import requests
import logging

from helpers.decorators import log_execution_time


class Sender:
    """
    A class that sends HTTP requests to the defined API endpoints.
    This class contains specific methods for each API operation.
    """
    base_url = "http://localhost:8000"
    logger = logging.getLogger('SenderLogger')
    logging.basicConfig(level=logging.INFO)

    @classmethod
    def send_request(cls, method: str, endpoint: str, data: dict = None, params: dict = None):
        """
        Generic method for sending HTTP requests and logging information about them.

        :param method: HTTP method (GET, POST, DELETE).
        :param endpoint: API endpoint (without base URL).
        :param data: Payload for POST requests (optional).
        :param params: Query parameters for GET requests (optional).
        :return: Response object.
        """
        url = f"{cls.base_url}/{endpoint}"
        cls.logger.info(f"Sending {method} request to {url} with data: {data} and params: {params}")

        if method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError("Unsupported HTTP method")

        cls.logger.info(f"Received response with status code: {response.status_code}")
        return response

    @classmethod
    def add_batch(cls, symbol: str, values: list):
        """
        Send a POST request to add a batch of trading prices for a given financial instrument.
        """
        endpoint = "add_batch"
        data = {"symbol": symbol, "values": values}
        return cls.send_request('POST', endpoint, data)

    @classmethod
    @log_execution_time
    def get_values(cls, symbol: str):
        """
        Send a GET request to retrieve trading values for a specific symbol.
        """
        endpoint = f"get_values/{symbol}"
        return cls.send_request('GET', endpoint)

    @classmethod
    @log_execution_time
    def delete_symbol(cls, symbol: str):
        """
        Send a DELETE request to remove a specific symbol from the database.
        """
        endpoint = f"delete_symbol/{symbol}"
        return cls.send_request('DELETE', endpoint)

    @classmethod
    @log_execution_time
    def clear_db(cls):
        """
        Send a DELETE request to clear the entire database.
        """
        endpoint = "clear_db"
        return cls.send_request('DELETE', endpoint)

    @classmethod
    @log_execution_time
    def get_stats(cls, symbol: str, k: int):
        """
        Send a GET request to retrieve statistical analysis of trading data for a specific symbol.

        :param symbol: The financial instrument's identifier.
        :param k: An integer specifying the number of last 1e{k} data points to analyze.
        :return: The response from the API, which includes statistics (min, max, last, avg, var).
        """
        endpoint = "stats"
        params = {"symbol": symbol, "k": k}
        return cls.send_request('GET', endpoint, params=params)
