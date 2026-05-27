from __future__ import annotations

from threading import Lock


class MetricsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self.requests_total = 0
        self.request_latency_ms = 0.0
        self.errors_total = 0
        self.events_total = 0
        self.scheduler_jobs_total = 0
        self.risk_halt_active = 0
        self.backtests_total = 0
        self.content_items_total = 0
        self.iot_actions_total = 0

    def increment_requests(self, latency_ms: float) -> None:
        with self._lock:
            self.requests_total += 1
            self.request_latency_ms += max(latency_ms, 0.0)

    def increment_errors(self) -> None:
        with self._lock:
            self.errors_total += 1

    def increment_events(self, count: int = 1) -> None:
        with self._lock:
            self.events_total += max(count, 0)

    def increment_scheduler_jobs(self, count: int = 1) -> None:
        with self._lock:
            self.scheduler_jobs_total += max(count, 0)

    def set_risk_halt_active(self, active: bool) -> None:
        with self._lock:
            self.risk_halt_active = 1 if active else 0

    def increment_backtests(self, count: int = 1) -> None:
        with self._lock:
            self.backtests_total += max(count, 0)

    def increment_content_items(self, count: int = 1) -> None:
        with self._lock:
            self.content_items_total += max(count, 0)

    def increment_iot_actions(self, count: int = 1) -> None:
        with self._lock:
            self.iot_actions_total += max(count, 0)

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            return {
                "zdash_requests_total": float(self.requests_total),
                "zdash_request_latency_ms": float(self.request_latency_ms),
                "zdash_errors_total": float(self.errors_total),
                "zdash_events_total": float(self.events_total),
                "zdash_scheduler_jobs_total": float(self.scheduler_jobs_total),
                "zdash_risk_halt_active": float(self.risk_halt_active),
                "zdash_backtests_total": float(self.backtests_total),
                "zdash_content_items_total": float(self.content_items_total),
                "zdash_iot_actions_total": float(self.iot_actions_total),
            }

    def reset(self) -> None:
        with self._lock:
            self.requests_total = 0
            self.request_latency_ms = 0.0
            self.errors_total = 0
            self.events_total = 0
            self.scheduler_jobs_total = 0
            self.risk_halt_active = 0
            self.backtests_total = 0
            self.content_items_total = 0
            self.iot_actions_total = 0


metrics_store = MetricsStore()


def render_metrics() -> str:
    snapshot = metrics_store.snapshot()
    lines = []
    for name, value in snapshot.items():
        lines.append(f"# HELP {name} zDash metric {name}")
        lines.append(f"# TYPE {name} gauge")
        lines.append(f"{name} {value}")
    return "\n".join(lines)
