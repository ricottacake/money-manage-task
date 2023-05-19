from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.account import ShowAccount
from app.api.schemas.credit import ShowCredit
from app.api.schemas.currency import ShowCurrency
from app.api.schemas.deposit import ShowDeposit
from app.db.dals import UserDAL, CreditDAL
from app.db.models import Deposit
from app.db.session import get_db

router = APIRouter(
    prefix=""
)


async def _get_user_accounts(db) -> Sequence[ShowAccount]:
    async with db as session:
        async with session.begin():
            account_dal = UserDAL(session)

            user_accounts = await account_dal.get_accounts()

            return tuple(ShowAccount(
                id=account.id,
                balance=account.balance,
                name=account.name,
                currency=ShowCurrency(
                    id=currency.id,
                    name=currency.name
                ),
                created_at=account.created_at
            ) for account, currency in user_accounts)


async def _get_user_credits(db) -> Sequence[ShowCredit]:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)

            account_credits = await credit_dal.get_user_credits()

            return tuple(ShowCredit(
                id=credit.id,
                name=credit.name,
                amount=credit.amount,
                account=ShowAccount(
                    id=account.id,
                    name=account.name,
                    balance=account.balance,
                    currency=ShowCurrency(
                        id=currency.id,
                        name=currency.name
                    ),
                    created_at=account.created_at
                ),
                is_open=credit.is_open
            ) for account, credit, currency in account_credits)


async def _get_user_deposits(db) -> Sequence[ShowDeposit]:
    async with db as session:
        async with session.begin():
            deposit_dal = Deposit(session)

            account_deposits = await deposit_dal.get_user_deposits()

            return tuple(ShowDeposit(
                id=deposit.id,
                name=deposit.name,
                amount=deposit.amount,
                account=ShowAccount(
                    id=account.id,
                    name=account.name,
                    balance=account.balance,
                    currency=ShowCurrency(
                        id=currency.id,
                        name=currency.name
                    ),
                    created_at=account.created_at
                ),
                is_open=deposit.is_open
            ) for account, deposit, currency in account_deposits)


@router.get("/accounts/")
async def get_user_accounts(db: AsyncSession = Depends(get_db)) -> Sequence[ShowAccount]:
    user_accounts = await _get_user_accounts(db=db)
    return user_accounts


@router.get("/credits/")
async def get_user_credits(db: AsyncSession = Depends(get_db)) -> Sequence[ShowCredit]:
    user_credits = await _get_user_credits(db=db)
    return user_credits


@router.get("/deposits/")
async def get_user_deposits(db: AsyncSession = Depends(get_db)) -> Sequence[ShowDeposit]:
    user_deposits = await _get_user_deposits(db=db)
    return user_deposits
