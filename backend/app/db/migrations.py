from sqlalchemy import text

from app.db.base import Base
import app.db.models  # noqa
from app.db.session import engine

# Import all models here so Base.metadata is populated
import app.billing.models  # noqa
import app.marketplace.models  # noqa
import app.enterprise.models  # noqa

def create_all() -> None:
    Base.metadata.create_all(bind=engine)


def run_migrations() -> None:
    # Lightweight compatibility migration path for Phase 08.1.
    create_all()


def check_database_connection() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
