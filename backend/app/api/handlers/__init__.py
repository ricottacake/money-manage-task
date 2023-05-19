from fastapi import APIRouter

from app.api.handlers import transaction, account, user, tag, transfer, credit, deposit


router = APIRouter(
    prefix="/api"
)

router.include_router(user.router)
router.include_router(account.router)
router.include_router(transaction.router)
router.include_router(tag.router)
router.include_router(transfer.router)
router.include_router(credit.router)
router.include_router(deposit.router)
