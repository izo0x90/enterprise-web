from fastapi import FastAPI
import uvicorn

app = FastAPI()

from . import api
from enterprise_web.repo import EntityRepoManager
from enterprise_web.infra import register_routes
from enterprise_web.integrations.web.fastapi import build_fastapi_register_route

from functools import partial

from .api.common.data_stores.sqlmodel import create_db_and_tables, get_db_session
from .api.common.data_stores.types import DataStoreTypes

repo = EntityRepoManager()

repo.session_getters_by_data_source_type[DataStoreTypes.MYSQL] = get_db_session

fastapi_register_route = build_fastapi_register_route(app)

register_routes(api, repo, fastapi_register_route, get_db_session)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/init_test_db")
async def root():
    from .api.project.data import models
    from sqlmodel import select
    create_db_and_tables()
    project = models.Project(project_name="Test project 0")
    with get_db_session() as session:
        session.add(project)
        session.commit()
        res = session.exec(select(models.Project)).all()
        print("DATA: ", res)

    return {"status": "Success"}

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
