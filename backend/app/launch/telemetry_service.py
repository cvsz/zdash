class TelemetryService:
    SECRET_KEYS = {"token", "password", "secret", "api_key"}

    def redact_payload(self, payload: dict) -> dict:
        return {k: ("[REDACTED]" if any(sk in k.lower() for sk in self.SECRET_KEYS) else v) for k, v in payload.items()}
