import pydantic

from enterprise_web.api.command import Command, CommandInput, CommandOutput
from enterprise_web.auth import Identity
from enterprise_web.infra import register_endpoint
from enterprise_web.repo import EntityRepoManager

from .feature_group import crud_commands
from .feature_group import crud_commands2

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


# Class based approach
@crud_commands2.register_command(command_name="create", version=1)
class CreateCommand(Command):
    def _check_permissions(
        self, identity: Identity, repo: EntityRepoManager, args: Input
    ) -> bool:
        return True

    def _handler(
        self, identity: Identity, repo: EntityRepoManager, args: Input
    ) -> Output:
        project_entity = repo["ProjectEntity"].get([args.id], [])[args.id]
        return Output(project_name=project_entity.name)

    def endpoint(
        self, identity: Identity, repo: EntityRepoManager, request_data: RequestData
    ) -> ResponseData:
        print("Project create end point START")
        inputs = Input(**request_data.model_dump())
        result = exec(identity, repo, inputs)
        print("Project create end point END")
        return ResponseData(project_name=result.project_name)


@crud_commands2.register_command(command_name="create", version=2)
class CC2(Command):
    def endpoint(
        self, identity: Identity, repo: EntityRepoManager, request_data: RequestData
    ) -> ResponseData:
        print("Project create end point START")
        inputs = Input(**request_data.model_dump())
        result = exec(identity, repo, inputs)
        print("Project create end point END")
        return ResponseData(project_name=result.project_name)


@crud_commands.register_command(command_name="create_on_curd", version=1)
class CCOnCrud(Command):
    def endpoint(
        self, identity: Identity, repo: EntityRepoManager, request_data: RequestData
    ) -> ResponseData:
        print("Project create end point START")
        inputs = Input(**request_data.model_dump())
        result = exec(identity, repo, inputs)
        print("Project create end point END")
        return ResponseData(project_name=result.project_name)


exec = CreateCommand().exec
# Class based approach END


# TODO: (Hristo) How do we handle HTTP response codes
# TODO: (Hristo) How do we handle endpoint registration, can this magic naming approach be acceptable
@register_endpoint(path="/test2", method="post")
def endpoint(
    identity: Identity, repo: EntityRepoManager, request_data: RequestData
) -> ResponseData:
    print("Project create end point START")
    inputs = Input(**request_data.model_dump())
    result = exec(identity, repo, inputs)
    print("Project create end point END")
    return ResponseData(project_name=result.project_name)
