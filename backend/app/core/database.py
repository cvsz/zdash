from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()
database_url = getattr(settings, 'database_url', 'sqlite:///./zdash.db')
connect_args = {'check_same_thread': False} if database_url.startswith('sqlite') else {}
engine = create_engine(database_url, echo=False, connect_args=connect_args)


@contextmanager
def session_scope():
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session
