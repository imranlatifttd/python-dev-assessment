import hashlib


def generate_mock_metrics(query_text: str) -> tuple[int, int]:
    """
    Generates deterministic mock search volume and difficulty based on the query hash.
    This ensures that running the same query multiple times
    yields the exact same mocked metrics.
    """
    # Create a stable integer from the query string
    hash_obj = hashlib.md5(query_text.encode('utf-8'))
    hash_int = int(hash_obj.hexdigest(), 16)

    # Volume between 10 and 10000
    volume = (hash_int % 9991) + 10

    # Difficulty between 0 and 100
    difficulty = (hash_int // 10000) % 101

    return volume, difficulty