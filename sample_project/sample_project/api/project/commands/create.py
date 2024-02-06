import pydantic

from enterprise_web.api.command import command, CommandInput, CommandOutput
from enterprise_web.auth import Identity
from enterprise_web.infra import register_endpoint
from enterprise_web.repo import EntityRepoManager

# TODO: (Hristo) How do we handle identity, permissions etc.


class Input(CommandInput):
    id: int
    project_name: str


class Output(CommandOutput):
    project_name: str


class RequestData(pydantic.BaseModel):
    id: int
    project_name: str


class ResponseData(pydantic.BaseModel):
    project_name: str


# Decorator based approach
def _check_permissions(
    identity: Identity, repo: EntityRepoManager, args: Input
) -> bool:
    return True


@command(_check_permissions)
def handler(identity: Identity, repo: EntityRepoManager, args: Input) -> Output:
    project_entity = repo["ProjectEntity"].get([args.id], [])[args.id]
    return Output(project_name=project_entity.name)


# Decorator based approach END


# TODO: (Hristo) How do we handle HTTP response codes
# TODO: (Hristo) How do we handle endpoint registration, can this magic naming approach be acceptable
@register_endpoint(path="/test", method="post")
def endpoint(
    identity: Identity, repo: EntityRepoManager, request_data: RequestData
) -> ResponseData:
    print("Project create end point START")
    inputs = Input(**request_data.model_dump())
    result = handler(identity, repo, inputs)
    print("Project create end point END")
    return ResponseData(project_name=result.project_name)
