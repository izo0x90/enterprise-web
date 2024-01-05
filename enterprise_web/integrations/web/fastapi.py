from functools import partial

def _fastapi_register_route(router_instance, action_type, url_path, handler):
    getattr(router_instance, action_type)(url_path)(handler)

def build_fastapi_register_route(router_instance):
    return partial(_fastapi_register_route, router_instance)
