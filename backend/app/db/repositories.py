from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User, AuditLog

class UserRepository:
    def __init__(self, db: Session): self.db = db
    def get_by_email(self, email: str): return self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    def count(self) -> int: return len(self.db.execute(select(User)).scalars().all())

class AuditRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, **kwargs):
        row = AuditLog(**kwargs); self.db.add(row); self.db.commit(); self.db.refresh(row); return row
