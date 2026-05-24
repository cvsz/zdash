def generate_signal(price: float, idx: int) -> int:
    return 1 if (idx % 10) > 4 else -1
