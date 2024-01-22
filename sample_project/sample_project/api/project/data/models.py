from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str = Field(index=True)
    # secret_name: str
    # age: Optional[int] = Field(default=None, index=True)
    #_version: How do we add sqlalch versioning to these models

