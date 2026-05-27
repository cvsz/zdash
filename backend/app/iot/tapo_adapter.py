from __future__ import annotations

from app.core.config import get_settings
from app.iot.base import IoTAdapter
from app.iot.models import IoTActionResult


class TapoAdapter(IoTAdapter):
    """Phase 04 Tapo adapter shell.

    Real Tapo control is intentionally not enabled in this phase. All behavior
    remains dry-run, mock, or explicitly blocked.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def _credentials_present(self) -> bool:
        return bool(
            self.settings.tapo_username
            and self.settings.tapo_password
            and self.settings.tapo_device_ip
        )

    def _simulated(
        self, device_alias: str, action: str, message: str, output: dict | None = None
    ) -> IoTActionResult:
        return IoTActionResult(
            ok=True,
            dry_run=True,
            device_alias=device_alias,
            action=action,  # type: ignore[arg-type]
            message=message,
            output=output or {},
        )

    def _blocked(
        self, device_alias: str, action: str, message: str, output: dict | None = None
    ) -> IoTActionResult:
        return IoTActionResult(
            ok=False,
            dry_run=bool(self.settings.iot_dry_run),
            device_alias=device_alias,
            action=action,  # type: ignore[arg-type]
            message=message,
            output=output or {},
        )

    def get_status(self, device_alias: str) -> IoTActionResult:
        configured = self._credentials_present()
        output = {
            "configured": configured,
            "device_ip": self.settings.tapo_device_ip or "not-configured",
            "adapter_mode": "dry_run" if self.settings.iot_dry_run else "adapter_shell",
        }
        if self.settings.iot_dry_run or not configured:
            reason = (
                "Dry-run status simulated."
                if self.settings.iot_dry_run
                else "Credentials missing; safe status mock returned."
            )
            return self._simulated(device_alias, "status", reason, output)

        return self._blocked(
            device_alias,
            "status",
            "Real Tapo status calls are not enabled in Phase 04 adapter shell.",
            output,
        )

    def turn_on(self, device_alias: str) -> IoTActionResult:
        if self.settings.iot_dry_run:
            return self._simulated(
                device_alias,
                "turn_on",
                "Dry-run turn_on simulated.",
                {"simulated": True},
            )

        if not self._credentials_present():
            return self._simulated(
                device_alias,
                "turn_on",
                "Missing Tapo credentials; safe turn_on simulation returned.",
                {"simulated": True},
            )

        return self._blocked(
            device_alias,
            "turn_on",
            "Real turn_on is blocked in Phase 04 adapter shell. Keep dry-run mode or implement approved provider integration.",
            {"blocked": True},
        )

    def turn_off(self, device_alias: str) -> IoTActionResult:
        if self.settings.iot_dry_run:
            return self._simulated(
                device_alias,
                "turn_off",
                "Dry-run turn_off simulated.",
                {"simulated": True},
            )

        if not self._credentials_present():
            return self._simulated(
                device_alias,
                "turn_off",
                "Missing Tapo credentials; safe turn_off simulation returned.",
                {"simulated": True},
            )

        return self._blocked(
            device_alias,
            "turn_off",
            "Real turn_off is blocked in Phase 04 adapter shell. Keep dry-run mode or implement approved provider integration.",
            {"blocked": True},
        )

    def power_cycle(
        self, device_alias: str, confirmation: bool = False
    ) -> IoTActionResult:
        if self.settings.iot_dry_run:
            return self._simulated(
                device_alias,
                "power_cycle",
                "Dry-run power_cycle simulated (turn_off -> wait -> turn_on).",
                {"sequence": ["turn_off", "wait", "turn_on"], "simulated": True},
            )

        if self.settings.iot_require_confirmation and not confirmation:
            return self._blocked(
                device_alias,
                "power_cycle",
                "Power cycle blocked: confirmation is required.",
                {"reason": "confirmation_required", "blocked": True},
            )

        if not self._credentials_present():
            return self._simulated(
                device_alias,
                "power_cycle",
                "Missing Tapo credentials; safe power_cycle simulation returned.",
                {"sequence": ["turn_off", "wait", "turn_on"], "simulated": True},
            )

        return self._blocked(
            device_alias,
            "power_cycle",
            "Real power_cycle is blocked in Phase 04 adapter shell. Use dry-run or approved integration in later phases.",
            {"blocked": True},
        )

    # Backward-compatible helper used by older API code.
    def connectivity_test(self) -> dict:
        status = self.get_status(self.settings.tapo_device_alias)
        return status.model_dump(mode="json")
