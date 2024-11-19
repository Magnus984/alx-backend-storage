#!/usr/bin/env python3
"""
A module with tools for request caching and tracking.
"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """
    Stores the output of fetched data in a cache.
    """
    @wraps(method)
    def wrapper(url) -> str:
        """
        The wrapper function to cache the output..
        """
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """
    Retrieves the content of a URL, caches the response,
    and logs the request.
    """
    return requests.get(url).text
