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


def call_history(method: Callable) -> Callable:
    """
    Store the history of inputs and outputs for a particular function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, str(output))
        return output
    return wrapper


def replay(fn: Callable) -> Callable:
    """
    Display history of calls of a particular function
    """
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class Cache:
    """Implements a cache with redis"""
    def __init__(self) -> None:
        """Initializes class."""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
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
