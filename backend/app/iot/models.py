from pydantic import BaseModel


class IoTActionRequest(BaseModel):
    action: str
    confirmation: bool = False


class IoTActionResult(BaseModel):
    ok: bool
    action: str
    dry_run: bool
    reason: str
