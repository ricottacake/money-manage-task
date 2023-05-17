from fastapi import APIRouter

from backend.api.handlers import transaction, account, user


router = APIRouter(
    prefix="/api"
)

router.include_router(transaction.router)
router.include_router(account.router)
router.include_router(user.router)
