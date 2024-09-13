import time


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
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        from main import LOG
        LOG.info(f"Execution time of {func.__name__.upper()}: {execution_time:.3f} milliseconds")
        return result

    return wrapper
