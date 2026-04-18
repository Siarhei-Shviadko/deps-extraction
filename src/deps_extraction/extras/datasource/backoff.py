import logging
from functools import wraps
from time import sleep
from typing import Any, Callable

__all__ = ["backoff", "retry_transaction"]

logger = logging.getLogger(__name__)


def backoff(
    start_sleep_time: float = 0.1,
    factor: int = 2,
    max_sleep_time: int = 6,
    times: int = 5,
):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time = start_sleep_time
            attempts = times
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    if not attempts:
                        raise
                    time = (time * 2**factor) if time < max_sleep_time else max_sleep_time
                    attempts -= 1
                    logger.error(
                        f"Error occured in {func.__name__}: {err}.\nTry to repeat {func.__name__}, "
                        + f"attempt # {times - attempts}. Delay before attempt: {time} sec.",
                    )
                sleep(time)

        return inner

    return func_wrapper


def retry_transaction(
    max_attempts: int = 15,
    initial_delay: float = 1,
    backoff_factor: float = 2,
    cutoff: float = 10,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts: int = 0
            delay: float = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if e.__class__.__name__ != "OperationalError":
                        raise

                    attempts += 1
                    if attempts >= max_attempts:
                        raise e

                    sleep(min(delay, cutoff))
                    delay *= backoff_factor

                    logger.error(f"Transaction failed. Retrying... Attempt {attempts}/{max_attempts}")

        return wrapper

    return decorator
