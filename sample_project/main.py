# TODO: Best way to structure a sample project in this repo, use the lib as proper dep.

from fastapi import FastAPI
import uvicorn

app = FastAPI()

from . import api
from enterprise_web.repo import EntityRepo
from enterprise_web.infra import register_routes
from enterprise_web.integrations.web.fastapi import build_fastapi_register_route

from functools import partial

repo = EntityRepo(entity_classes=api.project.domain.entities)

fastapi_register_route = build_fastapi_register_route(app)

register_routes(api, repo, fastapi_register_route)

@app.get("/")
async def root():
    return {"message": "Hello World"}

def start():
    uvicorn.run(
        "sample_project.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        # TODO: Add these settings in order for fastapi to be able to use the url schema of rev. proxy
        # proxy_headers=True,
        # forwarded_allow_ips='*' TODO: this should be the rev. proxy ip for production
    )
