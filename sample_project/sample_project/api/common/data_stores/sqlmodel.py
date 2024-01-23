from enterprise_web.repo import register_session_getter
from sqlmodel import (
    create_engine,
    Session,
    SQLModel
)

from .types import DataStoreTypes

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

sqlite_file_name = "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

@register_session_getter(DataStoreTypes.MYSQL)
def get_db_session():
    return Session(engine)

