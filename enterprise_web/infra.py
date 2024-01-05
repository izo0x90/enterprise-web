from functools import partial

def register_routes(package, repo, route_register_func):
    getmodule = partial(getattr, package)
    features = map(getmodule, package.__all__)
    for feature in features:
        for command_name in feature.commands.__all__:
            command = getattr(feature.commands, command_name)
            handler = partial(command.handler, repo)
            route_register_func('post', "/test", handler)

