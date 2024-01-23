import pydantic
from dataclasses import dataclass

from enterprise_web.repo import Entity
# TODO: (Hristo) How do we want to handle partially loaded objects for queries, How do we handle aggregations
# TODO: (Hristo) How do we handle batch updates

@dataclass
class ProjectDataModel:
    name: str
    id: int

class ProjectEntity(Entity):
    data: ProjectDataModel

    def __init__(self):
        self.data = ProjectDataModel(name="", id=0)

    @property
    def name(self):
        return self.data.name
        return self.data['project'].name

    @property
    def id(self):
        return self.data.id
        return self.data['project'].id

