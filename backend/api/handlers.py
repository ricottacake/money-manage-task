from fastapi import APIRouter


router = APIRouter(
    prefix="/api"
)


@router.get("/")
async def hello_world():
    return {
        "hello": "world"
    }
