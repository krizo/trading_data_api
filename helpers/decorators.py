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
        execution_time = round((end_time - start_time), 3) * 1000
        from main import LOG
        LOG.info(f"Execution time of {func.__name__.upper()}: {execution_time} milliseconds")
        return result

    return wrapper
