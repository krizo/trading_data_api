import random
import string
from typing import Iterable, Generator, List


class SymbolGenerator:
    _generated_symbols = []

    def __init__(self, length: int = 4):
        self.length = length

    def __next__(self):
        return self._generate_symbol()

    def _generate_symbol(self):
        while True:
            symbol = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(self.length))
            if symbol not in self._generated_symbols:
                return symbol


def chunk_data(data: Iterable[float], chunk_size: int) -> Generator[List[float], None, None]:
    """
    Divide the iterable `data` into chunks of `chunk_size`.

    :param data: Iterable (can be generator or list) of floating-point values.
    :param chunk_size: Maximum size of each chunk.
    :return: Generator yielding lists of floating-point numbers.
    """
    chunk = []
    for value in data:
        chunk.append(value)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []  # Reset chunk

    # Yield any remaining values if the last chunk is incomplete
    if chunk:
        yield chunk


def generate_values(num_values):
    """
    Generator that yields random trading values.
    """
    for _ in range(num_values):
        yield round(random.uniform(0.01, 1000.0), 2)
