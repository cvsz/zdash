from .models import PublicStatusComponent, PublicStatusIncident


class PublicStatusService:
    def __init__(self) -> None:
        self.components: dict[str, PublicStatusComponent] = {}
        self.incidents: dict[str, PublicStatusIncident] = {}

    def get_public_status_summary(self) -> dict:
        return {
            "components": [c.model_dump() for c in self.components.values()],
            "incidents": [
                {
                    "id": i.id,
                    "title": i.title,
                    "summary": i.summary,
                    "status": i.status,
                    "severity": i.severity,
                }
                for i in self.incidents.values()
                if i.public
            ],
        }
