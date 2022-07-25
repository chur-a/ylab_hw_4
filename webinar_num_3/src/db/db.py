from sqlmodel import Session, create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.core import config

__all__ = ("get_session", "engine", "Base")


engine = create_engine(config.DATABASE_URL, echo=True)


Base = declarative_base()


def get_session():
    with Session(engine) as session:
        yield session
