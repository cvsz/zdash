from __future__ import annotations

import json
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class MarketSessionPolicy:
    """Timezone-aware recurring sessions with operator-supplied holiday overrides.

    ``state`` returns (known, open). Unknown session state must be treated as
    closed by callers: fail closed.
    """

    def __init__(
        self,
        timezone_name: str,
        sessions: str,
        holidays: str = "",
        special_sessions_json: str = "",
    ) -> None:
        try:
            self.timezone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown market timezone: {timezone_name}") from exc
        self.sessions = self._parse_sessions(sessions)
        self.holidays = self._parse_holidays(holidays)
        self.special_sessions = self._parse_special_sessions(special_sessions_json)

    def state(self, now: datetime | None = None) -> tuple[bool, bool]:
        current = now or datetime.now(UTC)
        try:
            local = current.astimezone(self.timezone)
        except (ValueError, OverflowError):
            return False, False
        sessions, closed = self._sessions_for_date(local.date())
        if closed:
            return True, False
        current_time = local.timetz().replace(tzinfo=None)
        return True, any(start <= current_time <= end for start, end in sessions)

    def explain(self, now: datetime | None = None) -> dict[str, object]:
        current = now or datetime.now(UTC)
        try:
            local = current.astimezone(self.timezone)
        except (ValueError, OverflowError):
            return {
                "known": False,
                "open": False,
                "timezone": str(self.timezone),
                "reason": "invalid current time",
                "sessions": [],
            }
        day = local.date()
        sessions, closed = self._sessions_for_date(day)
        if day in self.special_sessions:
            source = "special"
            reason = "special session override" if sessions else "special closed date"
        elif day in self.holidays:
            source = "holiday"
            reason = "configured market holiday"
        elif day.weekday() >= 5:
            source = "weekend"
            reason = "weekend"
        else:
            source = "default"
            reason = "inside configured session" if not closed else "closed"
        current_time = local.timetz().replace(tzinfo=None)
        is_open = not closed and any(
            start <= current_time <= end for start, end in sessions
        )
        if not is_open and not closed and source in {"default", "special"}:
            reason = "outside configured session"
        return {
            "known": True,
            "open": is_open,
            "timezone": str(self.timezone),
            "local_time": local.isoformat(),
            "date": day.isoformat(),
            "source": source,
            "reason": reason,
            "holiday": day in self.holidays,
            "sessions": [
                f"{start.isoformat(timespec='minutes')}-"
                f"{end.isoformat(timespec='minutes')}"
                for start, end in sessions
            ],
        }

    def _sessions_for_date(self, day: date) -> tuple[list[tuple[time, time]], bool]:
        if day in self.special_sessions:
            sessions = self.special_sessions[day]
            return sessions, not sessions
        if day in self.holidays or day.weekday() >= 5:
            return [], True
        return self.sessions, False

    @staticmethod
    def _parse_holidays(raw: str) -> set[date]:
        holidays: set[date] = set()
        for item in raw.replace(";", ",").split(","):
            chunk = item.strip()
            if not chunk:
                continue
            try:
                holidays.add(date.fromisoformat(chunk))
            except ValueError as exc:
                raise ValueError(f"invalid market holiday date: {chunk}") from exc
        return holidays

    @classmethod
    def _parse_special_sessions(
        cls,
        raw: str,
    ) -> dict[date, list[tuple[time, time]]]:
        if not raw.strip():
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("special market sessions must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError(
                "special market sessions must be a JSON object keyed by date"
            )
        result: dict[date, list[tuple[time, time]]] = {}
        for raw_day, raw_sessions in payload.items():
            if not isinstance(raw_day, str):
                raise ValueError("special market session date keys must be strings")
            try:
                day = date.fromisoformat(raw_day)
            except ValueError as exc:
                raise ValueError(
                    f"invalid special market session date: {raw_day}"
                ) from exc
            if raw_sessions is None:
                result[day] = []
                continue
            if isinstance(raw_sessions, str):
                session_text = raw_sessions
            elif isinstance(raw_sessions, list) and all(
                isinstance(item, str) for item in raw_sessions
            ):
                session_text = ",".join(raw_sessions)
            else:
                raise ValueError(
                    f"special sessions for {raw_day} must be a string, "
                    "list of strings, or null"
                )
            result[day] = cls._parse_sessions(session_text, allow_empty=True)
        return result

    @staticmethod
    def _parse_sessions(
        raw: str,
        *,
        allow_empty: bool = False,
    ) -> list[tuple[time, time]]:
        sessions: list[tuple[time, time]] = []
        for item in raw.split(","):
            chunk = item.strip()
            if not chunk:
                continue
            start_raw, separator, end_raw = chunk.partition("-")
            if not separator:
                raise ValueError(f"invalid market session: {chunk}")
            try:
                start = time.fromisoformat(start_raw.strip())
                end = time.fromisoformat(end_raw.strip())
            except ValueError as exc:
                raise ValueError(f"invalid market session: {chunk}") from exc
            if end <= start:
                raise ValueError(f"market session end must follow start: {chunk}")
            sessions.append((start, end))
        if not sessions and not allow_empty:
            raise ValueError("at least one market session is required")
        return sessions
