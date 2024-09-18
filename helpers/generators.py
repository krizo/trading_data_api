import itertools
import random
import string
from typing import Iterable, Generator, List


class SymbolGenerator:
    def __init__(self, length: int = 4):
        """
        Initialize the SymbolGenerator with a specified symbol length.

        :param length: Length of the generated symbols (default is 4).
        """
        self.length = length
        self._generated_symbols = set()  # Use set for efficient lookups

    def __iter__(self):
        return self

    def __next__(self):
        return self._generate_symbol()

    def _generate_symbol(self) -> str:
        """
        Generate a unique symbol consisting of uppercase letters and digits.

        :return: A unique symbol.
        """
        while True:
            symbol = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(self.length))
            if symbol not in self._generated_symbols:
                self._generated_symbols.add(symbol)  # Keep track of generated symbols
                return symbol


def chunk_data(data: Iterable[float], chunk_size: int) -> List[List[float]]:
    """Helper function to split data into chunks."""
    it = iter(data)
    chunk = list(itertools.islice(it, chunk_size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, chunk_size))


def generate_values(num_values: int) -> Generator[float, None, None]:
    """
    Generator that yields random trading values.

    :param num_values: Number of values to generate.
    :return: Generator yielding random floating-point values.
    """
    for _ in range(num_values):
        yield round(random.uniform(0.01, 1000.0), 2)
