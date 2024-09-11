import time

from main import LOG


def log_execution_time(func):
    """
    Decorator to log the execution time of a function.
    :param func: Function to be decorated
    :return: Wrapped function
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        LOG.info(f"Execution time of {args[0].__name__}.{func.__name__.upper()}: {int(execution_time)} milliseconds")
        return result

    return wrapper
