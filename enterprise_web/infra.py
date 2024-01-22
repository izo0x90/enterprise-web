from functools import partial
import inspect

async def get_repo(repo):

    print("Repo session start")
    with repo.init_session():
        yield repo
        repo.update_mutated()


    print("Repo session end")

async def get_ident():
    return None

def register_routes(package, repo, route_register_func, get_db_session):
    getmodule = partial(getattr, package)
    features = map(getmodule, package.__all__)


    for feature in features:
        for command_name in feature.commands.__all__:
            command = getattr(feature.commands, command_name)
            handler = command.endpoint
            print("Annotations ", inspect.get_annotations(handler))
            print("In reg. routes", handler)
            route_register_func('post', "/test", handler, partial(get_repo, repo), get_ident)

