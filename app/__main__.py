from fastapi import FastAPI, APIRouter

from app.endpoints import routers


def add_specification_info(app: FastAPI):
    app.title = "Automatic testing programming tasks service"
    app.description = "Service for automatic testing student's programs in SibFU"
    app.version = "0.0.1"
    app.openapi_url = "/openapi"
    app.openapi_tags = [...]
    app.servers = [...]
    app.openapi_version = "3.1.0"

def add_routers(app: FastAPI, router_list: list[APIRouter]):
    app.root_path = ""
    for router in router_list:
        app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI()
    add_specification_info(app)
    add_routers(app, routers)
    return app


app = create_app()
