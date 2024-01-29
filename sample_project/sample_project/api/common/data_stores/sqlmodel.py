from enterprise_web.repo import register_session_getter
from sqlmodel import (
    create_engine,
    Session,
    SQLModel
)

from .types import DataStoreTypes

# TODO: (Hristo) Uneff all this nonsense when we decide how we want to handle import hierarchy
_engine = [None]

def create_db_and_tables():
    SQLModel.metadata.create_all(_engine[0])

def init_db():
    sqlite_file_name = "database.db"

    sqlite_url = f"sqlite:///{sqlite_file_name}"

    _engine[0] = create_engine(sqlite_url, echo=True)

@register_session_getter(DataStoreTypes.MYSQL)
def get_db_session():
    return Session(_engine[0])

