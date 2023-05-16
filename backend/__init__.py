from fastapi import FastAPI, APIRouter

from backend.api.handlers import router


ROUTERS: tuple[APIRouter] = (router,)


def create_app() -> FastAPI:
    app = FastAPI(
        title="MoneyManageTask"
    )

    for router in ROUTERS:
        app.include_router(router)

    return app
