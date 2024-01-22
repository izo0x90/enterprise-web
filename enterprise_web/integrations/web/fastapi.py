from functools import partial

from fastapi import Depends

def _fastapi_register_route(router_instance, action_type, url_path, handler, get_repo_func, get_ident_func):
    handler = partial(handler, identity=Depends(get_ident_func), repo=Depends(get_repo_func))
    # handler = partial(handler, repo=None)
    print(handler)
    getattr(router_instance, action_type)(url_path)(handler)
    # router_instance.add_route(url_path, handler, ['POST'])
    print('Adding route for', router_instance, url_path)

def build_fastapi_register_route(router_instance):
    return partial(_fastapi_register_route, router_instance)
