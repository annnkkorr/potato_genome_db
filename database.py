from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./data/potato.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Enable FK enforcement for every SQLite connection
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
