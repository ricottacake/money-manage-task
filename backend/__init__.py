from fastapi import FastAPI, APIRouter

from backend.api import handlers


ROUTERS: tuple[APIRouter] = (handlers.router,)


def create_app() -> FastAPI:
    app = FastAPI(
        title="MoneyManageTask"
    )

    for router in ROUTERS:
        app.include_router(router)

    return app
