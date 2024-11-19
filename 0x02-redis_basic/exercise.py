#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Callable, Union
from functools import wraps


def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Alters behavior of function by counting calls.
        """
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """Implements a cache with redis"""
    def __init__(self) -> None:
        """Initializes class."""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Sets data into redis database"""
        random_key = str(uuid.uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(
            self,
            key: str,
            fn: Callable = None
            ) -> Union[str, bytes, int, float]:
        """Gets data from redis database"""
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """
        Parameterizes get method with string conversion function.
        """
        return self.get(key, fn=lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        Parameterizes get method with integer conversion function.
        """
        return self.get(key, fn=int)
