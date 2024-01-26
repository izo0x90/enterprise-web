from functools import partial
import inspect

from .log import get_logger

logger = get_logger()

async def get_repo(repo):

    logger.debug("Repo session start")
    with repo.init_session():
        yield repo
        repo.update_mutated()


    logger.debug("Repo session end")

async def get_ident():
    return None

def register_routes(package, repo, route_register_func):
    getmodule = partial(getattr, package)
    features = map(getmodule, package.__all__)


    for feature in features:
        for command_name in feature.commands.__all__:
            command = getattr(feature.commands, command_name)
            handler = command.endpoint
            route_register_func(handler._method, handler._path, handler, partial(get_repo, repo), get_ident)

def register_endpoint(path, method='get'):
    def decorator_builder(f):
        f._path = path
        f._method = method
        return f
    return decorator_builder
