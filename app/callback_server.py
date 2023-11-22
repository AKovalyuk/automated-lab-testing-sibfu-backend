from fastapi import FastAPI

from app.endpoints import callback_server_router


app = FastAPI()
app.include_router(callback_server_router)
