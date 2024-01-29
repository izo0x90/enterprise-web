import logging

from fastapi import FastAPI, APIRouter
import uvicorn


from enterprise_web.repo import EntityRepoManager
from enterprise_web.infra import EnterpriseApp
from enterprise_web.integrations.web.fastapi import fastapi_register_route

from .api import project 
from .api.common import data_stores

logging.basicConfig(level=logging.DEBUG)

fastapi_app = FastAPI()

data_stores.sqlmodel.init_db()
repo = EntityRepoManager()

EnterpriseApp(repo=repo,
              web_route_register_func=fastapi_register_route,
              web_app=fastapi_app,
              web_router_csl=APIRouter,
              features=[
                  project.feature.project_feature
              ]
)

@fastapi_app.get("/")
async def root():
    return {"message": "Hello World"}

@fastapi_app.get("/init_test_db")
async def init_db_data():
    from .api.project.data import models
    from .api.common.data_stores.sqlmodel import create_db_and_tables
    from sqlmodel import select, Session
    create_db_and_tables()
    project = models.Project(project_name="Test project 0")
    with Session() as session:
        session.add(project)
        session.commit()
        res = session.exec(select(models.Project)).all()
        print("DATA: ", res)

    return {"status": "Success"}

def start():
    uvicorn.run(
        "sample_project.main:fastapi_app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        # TODO: Add these settings in order for fastapi to be able to use the url schema of rev. proxy
        # proxy_headers=True,
        # forwarded_allow_ips='*' TODO: this should be the rev. proxy ip for production
    )
