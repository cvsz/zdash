from typing import Any

BUFFER: list[Any] = []


def push(e):
    BUFFER.append(e)
    del BUFFER[:-500]


def recent():
    return BUFFER
