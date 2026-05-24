def generate_signal(price: float, idx: int) -> int:
    return 1 if idx % 5 in (1, 2) else 0
