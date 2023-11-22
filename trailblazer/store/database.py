from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

SESSION: Session | None = None
ENGINE: Engine | None = None

Model = declarative_base()


def initialize_database(db_uri: str) -> None:
    global SESSION, ENGINE
    ENGINE = create_engine(db_uri, pool_pre_ping=True)
    session_factory = sessionmaker(ENGINE)
    SESSION = scoped_session(session_factory)


def get_session() -> Session:
    return SESSION


def create_all_tables() -> None:
    """Create all tables in the database"""
    Model.metadata.create_all(bind=SESSION.get_bind())


def drop_all_tables() -> None:
    """Drop all tables in the database."""
    Model.metadata.drop_all(bind=SESSION.get_bind())


def get_tables() -> list[str]:
    """Get a list of all tables in the database."""
    inspector = inspect(ENGINE)
    return inspector.get_table_names()
