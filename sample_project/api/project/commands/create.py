import pydantic

from enterprise_web.repo import EntityRepoType

# TODO: How do we handle identity, permissions etc.

class RequestData(pydantic.BaseModel):
    pass

class ResponseData(pydantic.BaseModel):
    project_name: str

def handler(repo: EntityRepoType, args: RequestData) -> ResponseData:
    print(repo)

    project_entity = repo.repos['ProjectEntity'].by_id([12345])[0]
    print(project_entity.name)
    return ResponseData(project_name=project_entity.name)

