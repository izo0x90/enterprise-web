from abc import abstractmethod
import pydantic

from enterprise_web.infra import register_endpoint
from enterprise_web.repo import EntityRepoManager

# TODO: (Hristo) How do we handle identity, permissions etc.

# Framework
from typing import Any, NamedTuple 
CommandInput = NamedTuple
CommandOutput = NamedTuple
Identity = Any

class InsufficientPermissions(Exception):
    pass

class Command:
    """ If we go with class based"""
    @abstractmethod
    def _check_permissions(self, identity: Identity, repo: EntityRepoManager, args: Any) -> bool:
        raise NotImplemented

    @abstractmethod
    def _handler(self, identity: Identity, repo: EntityRepoManager, args: Any) -> CommandOutput:
        raise NotImplemented

    def exec(self, identity: Identity, repo: EntityRepoManager, args: CommandInput) -> Any:
        if not self._check_permissions(identity, repo, args):
            raise InsufficientPermissions

        return self._handler(identity, repo, args)

def command(check_permissions):
    """ Decorator approach """
    def decorator_builder(f):
        def wrapper(*args, **kwargs):
            if not check_permissions(*args, **kwargs):
                raise InsufficientPermissions
            return f(*args, **kwargs)

        return wrapper
    return decorator_builder
# Framework END

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
class CreateCommand(Command):
    def _check_permissions(self, identity: Identity, repo: EntityRepoManager, args: Input) -> bool:
        return True

    def _handler(self, identity: Identity, repo: EntityRepoManager, args: Input) -> Output:
        project_entity = repo['ProjectEntity'].get([args.id], [])[args.id]
        return Output(project_name=project_entity.name)

exec = CreateCommand().exec
# Class based approach END


# Decorator based approach
def _check_permissions(identity: Identity, repo: EntityRepoManager, args: Input) -> bool:
    return True

@command(_check_permissions)
def handler(identity: Identity, repo: EntityRepoManager, args: Input) -> Output:
    project_entity = repo['ProjectEntity'].get([args.id], [])[args.id]
    return Output(project_name=project_entity.name)
# Decorator based approach END

# TODO: (Hristo) How do we handle HTTP response codes
# TODO: (Hristo) How do we handle endpoint registration, can this magic naming approach be acceptable
@register_endpoint(path="/test", method="post")
def endpoint(identity: Identity, repo: EntityRepoManager, request_data: RequestData) -> ResponseData:
    print('Project create end point START')
    inputs = Input(**request_data.model_dump())
    result = exec(identity, repo, inputs)
    result_2 = handler(identity, repo, inputs)
    print('Project create end point END')
    return ResponseData(project_name=result.project_name)
