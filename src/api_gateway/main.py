from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from context import app

from api.v1.routes.account_route import router as account_router_v1
from api.v1.routes.user_route import router as user_router_v1
from api.v1.routes.cargo_route import router as cargo_router_v1


app.include_router(account_router_v1)
app.include_router(user_router_v1)
app.include_router(cargo_router_v1)

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("API_HOST", "localhost"),
        port=int(os.environ.get("API_PORT", 8000)),
    )
