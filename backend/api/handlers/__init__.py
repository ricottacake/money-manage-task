from fastapi import APIRouter

from backend.api.handlers import transaction, account


router = APIRouter(
    prefix="/api"
)

router.include_router(transaction.router)
router.include_router(account.router)
