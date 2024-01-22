import pydantic
from dataclasses import dataclass

# TODO: How do we want to handle partially loaded objects for queries, How do we handle aggregations
# TODO: How do we handle batch updates

@dataclass
class ProjectDataModel:
    # TODO: Where do these data models live, datalayer, integrates with the pydantic sql lib idea
    name: str
    id: int

class ProjectEntity:
    # models: list[type(pydantic.BaseModel)] = [ProjectDataModel]
    # data: dict[str, pydantic.BaseModel]
    data: ProjectDataModel

    def __init__(self):
        self.data = ProjectDataModel(name="", id=0)

    @property
    def name(self):
        return self.data.project_name
        return self.data['project'].name

    @property
    def id(self):
        return self.data.id
        return self.data['project'].id

