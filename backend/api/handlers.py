import uuid
from datetime import datetime

from fastapi import APIRouter

from backend.api.schemas import AccountCreate, ShowAccount, ShowCurrency, CurrencyCreate


router = APIRouter(
    prefix="/api"
)


@router.post("/account")
async def create_account(acc: AccountCreate, cur: CurrencyCreate) -> ShowAccount:
    return ShowAccount(
        id=uuid.uuid4(),
        name=acc.name,
        balance=acc.balance,
        currency=ShowCurrency(
            id=1,
            name=cur.name
        ),
        timestamp=datetime.utcnow()
    )
