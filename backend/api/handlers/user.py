import uuid
from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import ShowAccount
from backend.db.dals import UserDAL
from backend.db.session import get_db

router = APIRouter(
    prefix=""
)


async def _get_user_accounts(db) -> Sequence[ShowAccount] | None:
    async with db as session:
        async with session.begin():
            account_dal = UserDAL(session)

            user_accounts = await account_dal.get_accounts()

            return tuple(ShowAccount(
                id=account.id,
                balance=account.balance,
                name=account.name,
                currency_id=account.currency_id,
                created_at=account.created_at
            ) for account in user_accounts)


@router.get("/accounts")
async def get_account_transactions(db: AsyncSession = Depends(get_db)) -> Sequence[ShowAccount]:
    user_accounts = await _get_user_accounts(
        db=db
    )

    return user_accounts


