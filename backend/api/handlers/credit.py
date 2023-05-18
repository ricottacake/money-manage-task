import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import ShowAccount
from backend.api.schemas.credit import CreateCreditRequest, CreatedCreditResponse, ShowCredit, \
    ClosedCreditResponse, CloseCreditRequest, UpdateCreditRequest, UpdatedCreditResponse
from backend.api.schemas.currency import ShowCurrency
from backend.db.dals import CreditDAL, AccountDAL, CurrencyDAL
from backend.db.session import get_db


router = APIRouter(
    prefix="/credit"
)


async def _create_new_credit(request_body: CreateCreditRequest, db) -> CreatedCreditResponse:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)
            credit, transaction = await credit_dal.create_credit(
                name=request_body.name,
                amount=request_body.amount,
                account_id=request_body.account_id,
                tag_id=request_body.tag_id
            )
            return CreatedCreditResponse(
                created_credit_id=credit.id,
                created_credit_transaction_id=transaction.id
            )


async def _get_account_credits(account_id: uuid.UUID, db) -> Sequence[ShowCredit]:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)

            account_credits = await credit_dal.get_account_credits(account_id=account_id)

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


async def _get_credit_by_id(credit_id: uuid.UUID, db) -> ShowCredit:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)

            credit = await credit_dal.get_credit_by_id(
                credit_id=credit_id
            )

            account = await AccountDAL(session).get_account_by_id(credit.account_id)
            currency = await CurrencyDAL(session).get_currency_by_id(account.currency_id)

            return ShowCredit(
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
            )


async def _update_credit(
        credit_id: uuid.UUID, db, request_body: UpdateCreditRequest
) -> UpdatedCreditResponse:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)

            updated_credit_id = await credit_dal.update_credit(
                credit_id=credit_id,
                name=request_body.name
            )

            return UpdatedCreditResponse(
                updated_credit_id=updated_credit_id
            )


async def _close_credit(request_body: CloseCreditRequest, db) -> ClosedCreditResponse:
    async with db as session:
        async with session.begin():
            credit_dal = CreditDAL(session)

            closed_credit_id, created_credit_transaction = await credit_dal.close_credit(
                credit_id=request_body.credit_id
            )

            return ClosedCreditResponse(
                closed_credit_id=closed_credit_id,
                created_credit_transaction_id=created_credit_transaction.id
            )


@router.get("/all/")
async def get_account_credits(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Sequence[ShowCredit]:
    return await _get_account_credits(account_id, db=db)


@router.get("/", response_model=ShowCredit)
async def get_credit(credit_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ShowCredit:
    try:
        credit = await _get_credit_by_id(credit_id, db=db)
    except HTTPException as exception:
        raise exception
    return credit


@router.post("/", response_model=CreatedCreditResponse)
async def create_credit(
        request_body: CreateCreditRequest, db: AsyncSession = Depends(get_db)
) -> CreatedCreditResponse:
    created_credit_response = await _create_new_credit(request_body, db=db)
    return created_credit_response


@router.patch("/", response_model=UpdatedCreditResponse)
async def update_credit(
        credit_id: uuid.UUID, request_body: UpdateCreditRequest, db: AsyncSession = Depends(get_db)
) -> UpdatedCreditResponse:
    updated_credit_response = await _update_credit(
        credit_id=credit_id, request_body=request_body, db=db
    )
    return updated_credit_response


@router.post("/close/", response_model=ClosedCreditResponse)
async def close_credit(
        request_body: CloseCreditRequest, db: AsyncSession = Depends(get_db)
) -> ClosedCreditResponse:
    closed_credit_response = await _close_credit(request_body, db=db)
    return closed_credit_response
