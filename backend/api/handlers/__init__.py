from fastapi import APIRouter

from backend.api.handlers import transaction, account, user, tag, transfer


router = APIRouter(
    prefix="/api"
)

router.include_router(user.router)
router.include_router(account.router)
router.include_router(transaction.router)
router.include_router(tag.router)
router.include_router(transfer.router)
