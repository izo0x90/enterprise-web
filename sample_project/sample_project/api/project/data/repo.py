from enterprise_web.repo import (
    EntityRepo
)
from sqlmodel import select, col

from sample_project.api.common.data_stores.types import DataStoreTypes
from .models import Project
from ..domain.project_entity import ProjectEntity 

class ProjectEntityRepo(EntityRepo):
    ENTITY_CLS = ProjectEntity
    DATA_STORE_TYPE = DataStoreTypes.MYSQL

    def by_ids(self,  ids: list[int]) -> list['Entity']: 
        entities = []
        print(f"Current DB session is {self.db_session}")
        statement = select(Project).where(col(Project.id).in_(ids))
        populated_models = self.db_session.exec(statement).all()

        for model in populated_models:
            entity = self.ENTITY_CLS()
            entity.data.id = model.id
            entity.data.project_name = model.project_name
            entities.append(entity)

        return entities

