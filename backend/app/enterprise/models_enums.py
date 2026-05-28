from enum import Enum

class LicenseStatus(str, Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"

class ExportStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
