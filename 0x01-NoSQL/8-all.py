#!/usr/bin/env python3
"""List all documents in Python"""
from pymongo import MongoClient
from typing import List


def list_all(mongo_collection) -> List[str]:
    """ lists all documents in a collection"""
    return [doc for doc in mongo_collection.find()]
