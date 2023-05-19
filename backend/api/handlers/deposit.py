import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import ShowAccount
from backend.api.schemas.deposit import CreateDepositRequest, CreatedDepositResponse, ShowDeposit, \
    ClosedDepositResponse, CloseDepositRequest, UpdateDepositRequest, UpdatedDepositResponse
from backend.api.schemas.currency import ShowCurrency
from backend.db.dals import DepositDAL, AccountDAL, CurrencyDAL
from backend.db.session import get_db


router = APIRouter(
    prefix="/deposit"
)


async def _create_new_deposit(request_body: CreateDepositRequest, db) -> CreatedDepositResponse:
    async with db as session:
        async with session.begin():
            deposit_dal = DepositDAL(session)
            deposit, transaction = await deposit_dal.create_deposit(
                name=request_body.name,
                amount=request_body.amount,
                account_id=request_body.account_id,
                tag_id=request_body.tag_id
            )
            return CreatedDepositResponse(
                created_deposit_id=deposit.id,
                created_deposit_transaction_id=transaction.id
            )


async def _get_account_deposits(account_id: uuid.UUID, db) -> Sequence[ShowDeposit]:
    async with db as session:
        async with session.begin():
            deposit_dal = DepositDAL(session)

            account_deposits = await deposit_dal.get_account_deposits(account_id=account_id)

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


async def _get_deposit_by_id(deposit_id: uuid.UUID, db) -> ShowDeposit:
    async with db as session:
        async with session.begin():
            deposit_dal = DepositDAL(session)

            deposit = await deposit_dal.get_deposit_by_id(
                deposit_id=deposit_id
            )

            account = await AccountDAL(session).get_account_by_id(deposit.account_id)
            currency = await CurrencyDAL(session).get_currency_by_id(account.currency_id)

            return ShowDeposit(
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
            )


async def _update_deposit(
        deposit_id: uuid.UUID, db, request_body: UpdateDepositRequest
) -> UpdatedDepositResponse:
    async with db as session:
        async with session.begin():
            deposit_dal = DepositDAL(session)

            updated_deposit_id = await deposit_dal.update_deposit(
                deposit_id=deposit_id,
                name=request_body.name
            )

            return UpdatedDepositResponse(
                updated_deposit_id=updated_deposit_id
            )


async def _close_deposit(request_body: CloseDepositRequest, db) -> ClosedDepositResponse:
    async with db as session:
        async with session.begin():
            deposit_dal = DepositDAL(session)

            closed_deposit_id, created_deposit_transaction = await deposit_dal.close_deposit(
                deposit_id=request_body.deposit_id
            )

            return ClosedDepositResponse(
                closed_deposit_id=closed_deposit_id,
                created_deposit_transaction_id=created_deposit_transaction.id
            )


@router.get("/all/")
async def get_account_deposits(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Sequence[ShowDeposit]:
    return await _get_account_deposits(account_id, db=db)


@router.get("/", response_model=ShowDeposit)
async def get_deposit(deposit_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ShowDeposit:
    try:
        deposit = await _get_deposit_by_id(deposit_id, db=db)
    except HTTPException as exception:
        raise exception
    return deposit


@router.post("/", response_model=CreatedDepositResponse)
async def create_deposit(
        request_body: CreateDepositRequest, db: AsyncSession = Depends(get_db)
) -> CreatedDepositResponse:
    created_deposit_response = await _create_new_deposit(request_body, db=db)
    return created_deposit_response


@router.patch("/", response_model=UpdatedDepositResponse)
async def update_deposit(
        deposit_id: uuid.UUID, request_body: UpdateDepositRequest,
        db: AsyncSession = Depends(get_db)
) -> UpdatedDepositResponse:
    updated_deposit_response = await _update_deposit(
        deposit_id=deposit_id, request_body=request_body, db=db
    )
    return updated_deposit_response


@router.post("/close/", response_model=ClosedDepositResponse)
async def close_deposit(
        request_body: CloseDepositRequest, db: AsyncSession = Depends(get_db)
) -> ClosedDepositResponse:
    closed_deposit_response = await _close_deposit(request_body, db=db)
    return closed_deposit_response
