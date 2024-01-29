from enum import Enum
from typing import Callable, Self, TypeVar

from enterprise_web.dev import NEEDSTYPEHINT

class FeatureTypes(Enum):
    API = 'api' 

class FeatureGroupNameAlreadyRegistered(Exception):
    pass

class CommandNameAndVersionAlreadyRegistered(Exception):
    pass

FeatureGroupOrSubclass = TypeVar("FeatureGroupOrSubclass", bound="FeatureGroup")

class FeatureGroup:
    def __repr__(self) -> str:
        return super().__repr__() + f" {self.name}"

    # TODO: (Hristo) Checks for name characters valid for url path, groups, commands, queries
    def __init__(self, group_name: str) -> None:
        self.command_groups = {}
        self.query_groups = {}
        self.commands = {}
        self.queries = {}
        self.name = group_name

    def add_command_group(self, command_group: FeatureGroupOrSubclass) -> None:
        if command_group.name not in self.command_groups:
            self.command_groups[command_group.name] = command_group
            return

        raise FeatureGroupNameAlreadyRegistered

    def add_query_group(self, query_group: Self):
        raise NotImplemented

    
    def register_command(self, command_name: str, version: int) -> Callable:
        def do_registration(cls: NEEDSTYPEHINT) -> NEEDSTYPEHINT:
            if command_name not in self.commands or version not in self.commands[command_name]:
                self.commands.setdefault(command_name, {})[version] = cls

                print(self.commands)

                return cls

            raise CommandNameAndVersionAlreadyRegistered
        return do_registration


class ApiFeature(FeatureGroup):
    feature_type: FeatureTypes = FeatureTypes.API
