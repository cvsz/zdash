def generate_signal(price: float, idx: int) -> int:
    return 1 if idx % 3 != 0 else -1
