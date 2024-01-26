from functools import partial

from fastapi import Depends

from ...log import get_logger

logger = get_logger()

def _fastapi_register_route(router_instance, action_type, url_path, handler, get_repo_func, get_ident_func):
    handler = partial(handler, identity=Depends(get_ident_func), repo=Depends(get_repo_func))
    getattr(router_instance, action_type)(url_path)(handler)

    logger.debug(
            "Adding route, router: "
            f"`{router_instance}`, url: `{url_path}`, http method: `{action_type}` "
            f"handler: `{handler}`"
    )

def build_fastapi_register_route(router_instance):
    return partial(_fastapi_register_route, router_instance)
