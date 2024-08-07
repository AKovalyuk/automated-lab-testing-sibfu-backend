import os

from fastapi import FastAPI, APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints import routers
from app.config import settings


def add_specification_info(app: FastAPI):
    app.title = "Automatic testing programming tasks service"
    app.description = ("Service for automatic testing student's programs in SibFU\n"
                       f"Branch {os.getenv('BRANCH')}, commit {os.getenv('COMMIT_SHA')}")
    app.version = "0.0.1"
    app.servers = [
        {
            "url": f"http://127.0.0.1:{settings.APP_PORT}",
            "description": "Development server",
        }
    ]
    app.openapi_version = "3.1.0"


def add_routers(app: FastAPI, router_list: list[APIRouter]):
    for router in router_list:
        app.include_router(router, prefix=settings.PATH_PREFIX)


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None)
    add_specification_info(app)
    add_routers(app, routers)
    app.mount(
        path=settings.PATH_PREFIX + settings.STATIC_URL,
        app=StaticFiles(directory=settings.STATIC_FILES_DIR),
        name="static",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()


@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        title=app.title,
        openapi_url=app.openapi_url,
        # Custom CDN source for swagger-ui
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )
