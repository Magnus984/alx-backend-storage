#!/usr/bin/env python3
"""Log stats"""


def display_log_stats():
    """
    provides some stats about Nginx logs stored in MongoDB
    """
    client = MongoClient()
    nginx = client.logs.nginx

    print(nginx.count_documents({}), "logs")
    print("Methods:")

    for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        print(
            f"\tmethod {method}: {nginx.count_documents({'method': method})}"
        )

    print(f"{nginx.count_documents({'path': '/status'})} status check")


if __name__ == "__main__":
    display_log_stats()
