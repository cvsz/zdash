def sanitize_payload(payload: dict) -> dict:
    return {
        k: v
        for k, v in payload.items()
        if "token" not in k.lower() and "password" not in k.lower()
    }
