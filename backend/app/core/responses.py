from datetime import datetime, timezone
from typing import Any


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def ok(data: dict[str, Any]) -> dict[str, Any]:
    return {
        'ok': True,
        'data': data,
        'error': None,
        'timestamp': _timestamp(),
    }


def fail(code: str, message: str) -> dict[str, Any]:
    return {
        'ok': False,
        'data': None,
        'error': {
            'code': code,
            'message': message,
        },
        'timestamp': _timestamp(),
    }
