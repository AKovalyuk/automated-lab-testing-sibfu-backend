from fastapi import FastAPI

from app.endpoints import callback_server_router


app = FastAPI()
# Service for processing responses from judge0
app.include_router(callback_server_router)
