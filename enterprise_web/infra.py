from functools import partial
from typing import (
    Callable,
    Optional,
    Self,
    TypeVar
)

from pydantic import BaseModel


from .api.feature import ApiFeature, FeatureTypes
from .auth import Identity
from .dev import NEEDSTYPEHINT
from .log import get_logger
from .repo import (
   EntityRepoManager 
)

logger = get_logger()

EndpointReturnType = TypeVar('EndpointReturnType', bound=BaseModel)
EndpointHandler = Callable[[Identity, EntityRepoManager, BaseModel], EndpointReturnType]
Feature = ApiFeature | NEEDSTYPEHINT

async def get_repo(repo):

    logger.debug("Repo session start")
    with repo.init_session():
        yield repo
        repo.update_mutated()


    logger.debug("Repo session end")

async def get_ident():
    return None

# TODO: (Hristo) Remove this if we prefer the decorator approach
# def register_routes(package, repo, route_register_func):
#     getmodule = partial(getattr, package)
#     features = map(getmodule, package.__all__)
#
#
#     for feature in features:
#         for command_name in feature.commands.__all__:
#             command = getattr(feature.commands, command_name)
#             handler = command.endpoint
#             route_register_func(handler._method, handler._path, handler, partial(get_repo, repo), get_ident)

class Router(object):
    def __init__(self, name) -> None:
        self.name = name
        self.sub_paths = []
        self.handlers = []

    def include_router(self, router):
        self.sub_paths.append(router.name)

    def add_handelr(self, handler):
        self.handlers.append(handler)


class EnterpriseApp:
    _instance: Optional[Self] = None
    _endpoints = []

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance:
            return cls._instance
        else:
            return super().__new__(cls)

        
    def __init__(self,
                 repo: EntityRepoManager,
                 web_route_register_func: NEEDSTYPEHINT,
                 web_app: NEEDSTYPEHINT,
                 web_router_csl: NEEDSTYPEHINT,
                 features: list[Feature]):
        # TODO: (Hristo) define some interfaces to generically typehint web app/ routing concepts
        # TODO: (Hristo) Verify this actually recursses full routing tree
        # TODO: (Hristo) Error checking, double registering etc. (crosses over with api/feature.py)
        # TODO: (Hristo) api/V{?} structured portion of URL configurable ?

        self.repo = repo
        for method, path, handler in self._endpoints:
            web_route_register_func(web_app, method, path, handler, partial(get_repo, repo), get_ident)

        api_router = web_router_csl(prefix=f"/{FeatureTypes.API.value}")

        for idx, feature in enumerate(features):
            if feature.feature_type == FeatureTypes.API:

                command_groups_stack = [(feature, list(feature.command_groups.values()))]
                routers_at_level = {}
                current_group = None

                while command_groups_stack:
                    parent_group, current_level = command_groups_stack.pop()

                    if current_level:
                        current_group = current_level.pop()
                        command_groups_stack.append((parent_group, current_level))
                    else:
                        current_group = None
                        new_routers = {}
                        for version, child_routers in routers_at_level.items():
                            parent_router = web_router_csl(prefix=f"/{parent_group.name}")
                            for child_router in child_routers:
                                parent_router.include_router(child_router)

                            new_routers[version] = [parent_router]

                        routers_at_level = new_routers

                        continue

                    if current_group.command_groups:
                        command_groups_stack.append((current_group, list(current_group.command_groups.values())))

                    group_routers = {}
                    for command_name, command in current_group.commands.items():
                        for version, handler_cls in command.items():
                            if version not in group_routers.keys():
                                group_routers[version] = web_router_csl(prefix=f"/{current_group.name}")

                            command_handelr_instance = handler_cls()
                            path = f"/{command_name}"
                            handler = command_handelr_instance.endpoint
                            # TODO: (Hristo) Handle passing of http method type
                            web_route_register_func(group_routers[version], "post", path, handler, partial(get_repo, repo), get_ident)

                    for version, group_router in group_routers.items():
                        routers_at_level.setdefault(version, []).append(group_router)

                for version, routers in routers_at_level.items():
                    version_router = web_router_csl(prefix=f"/V{version}")

                    for feature_router in routers:
                        version_router.include_router(feature_router)
                    api_router.include_router(version_router)

        app_router = web_app
        app_router.include_router(api_router)
        


def register_endpoint(path: str, method: str='get'):
    def decorator_builder(handler: EndpointHandler):
        EnterpriseApp._endpoints.append((method, path, handler))
        return handler
    return decorator_builder
