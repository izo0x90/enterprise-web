from abc import abstractmethod
from typing import Any, NamedTuple

from enterprise_web.auth import Identity, InsufficientPermissions
from enterprise_web.repo import EntityRepoManager

CommandInput = NamedTuple
CommandOutput = NamedTuple


class Command:
    """If we go with class based"""

    @abstractmethod
    def _check_permissions(
        self, identity: Identity, repo: EntityRepoManager, args: Any
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _handler(
        self, identity: Identity, repo: EntityRepoManager, args: Any
    ) -> CommandOutput:
        raise NotImplementedError

    def exec(
        self, identity: Identity, repo: EntityRepoManager, args: CommandInput
    ) -> Any:
        if not self._check_permissions(identity, repo, args):
            raise InsufficientPermissions

        return self._handler(identity, repo, args)


def command(check_permissions):
    """Decorator approach"""

    def decorator_builder(f):
        def wrapper(*args, **kwargs):
            if not check_permissions(*args, **kwargs):
                raise InsufficientPermissions
            return f(*args, **kwargs)

        return wrapper

    return decorator_builder
