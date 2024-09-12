from typing import Generator, List


def chunk_data(data: List[float], chunk_size: int) -> Generator[List[float], None, None]:
    """
    Divide the list `data` into chunks of `chunk_size`.

    :param data: List of floating-point values representing prices.
    :param chunk_size: Maximum size of each chunk.
    :return: Generator yielding lists of floating-point numbers.
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]