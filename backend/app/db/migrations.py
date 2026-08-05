from sqlalchemy import text

# Import all models here so Base.metadata is populated
import app.billing.models
import app.db.models
import app.enterprise.models
import app.marketplace.models  # noqa
from app.db.base import Base
from app.db.session import engine


def create_all() -> None:
    Base.metadata.create_all(bind=engine)


def run_migrations() -> None:
    # Lightweight compatibility migration path for Phase 08.1.
    create_all()


def check_database_connection() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
