from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.scheduler import CreateJobRequest
from app.scheduler.scheduler_service import get_scheduler_service


class FridayAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="friday",
            name="Isla Grant",
            role="scheduler_automation",
            metadata={"tier": "rare", "legacy_name": "Friday"},
        )

    @property
    def scheduler(self):
        return get_scheduler_service()

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event(
            "friday.command.received",
            "Isla Grant received command message",
            message.model_dump(),
        )
        return self.run_task(task=message.message, context=message.context)

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        context = context or {}
        self.status = "running"
        try:
            if task == "health":
                result = self.health_check()
            elif task == "list_jobs":
                result = {
                    "jobs": [job.model_dump(mode="json") for job in self.list_jobs()]
                }
            elif task == "create_job":
                result = {"job": self.create_job(context).model_dump(mode="json")}
            elif task == "run_job":
                result = {
                    "result": self.run_job(str(context.get("job_id"))).model_dump(
                        mode="json"
                    )
                }
            elif task == "pause_job":
                result = {
                    "job": self.pause_job(str(context.get("job_id"))).model_dump(
                        mode="json"
                    )
                }
            elif task == "resume_job":
                result = {
                    "job": self.resume_job(str(context.get("job_id"))).model_dump(
                        mode="json"
                    )
                }
            elif task == "delete_job":
                result = {"deleted": self.delete_job(str(context.get("job_id")))}
            else:
                raise ValueError(f"Unsupported Isla Grant task: {task}")

            self.status = "idle"
            self.emit_event(
                "friday.command.completed",
                "Isla Grant completed command",
                {"task": task},
            )
            return {"task": task, "ok": True, **result}
        except Exception as exc:
            self.status = "error"
            self.emit_event(
                "friday.command.failed",
                "Isla Grant command failed",
                {"task": task, "error": str(exc)},
            )
            raise

    def list_jobs(self):
        return self.scheduler.list_jobs()

    def create_job(self, request: CreateJobRequest | dict[str, Any]):
        req = (
            request
            if isinstance(request, CreateJobRequest)
            else CreateJobRequest.model_validate(request)
        )
        return self.scheduler.create_job(req)

    def run_job(self, job_id: str):
        return self.scheduler.run_job(job_id, manual=True)

    def pause_job(self, job_id: str):
        return self.scheduler.pause_job(job_id)

    def resume_job(self, job_id: str):
        return self.scheduler.resume_job(job_id)

    def delete_job(self, job_id: str) -> bool:
        return self.scheduler.delete_job(job_id)

    def health_check(self) -> dict[str, Any]:
        base = super().health_check()
        base["scheduler"] = self.scheduler.get_status()
        return base
