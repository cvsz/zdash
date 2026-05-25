from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine
import app.db.models  # noqa

def create_all() -> None:
    Base.metadata.create_all(bind=engine)

def run_migrations() -> None:
    create_all()

def check_database_connection() -> bool:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    return True
