from __future__ import annotations

DEFAULT_ALERT_RULE_DEFINITIONS = [
    {
        "name": "risk emergency stop triggered",
        "event_type": "risk.kill_switch.activated",
        "severity": "critical",
    },
    {
        "name": "risk halt activated",
        "event_type": "risk.halt.activated",
        "severity": "warning",
    },
    {
        "name": "worker task failed",
        "event_type": "worker.task.failed",
        "severity": "warning",
    },
    {
        "name": "scheduler job failed",
        "event_type": "scheduler.job.failed",
        "severity": "warning",
    },
    {
        "name": "content publish blocked",
        "event_type": "content.publish.blocked",
        "severity": "warning",
    },
    {
        "name": "IoT action blocked",
        "event_type": "iot.action.blocked",
        "severity": "warning",
    },
    {
        "name": "auth login failure spike",
        "event_type": "auth.login.failure_spike",
        "severity": "critical",
    },
    {
        "name": "production safety blocker",
        "event_type": "production.safety.blocked",
        "severity": "critical",
    },
]
