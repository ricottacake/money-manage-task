import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import AccountCreate, ShowAccount, \
    UpdateAccountRequest, UpdatedAccountResponse, DeletedAccountResponse, CreatedAccountResponse, \
    GetAccountTransactionsRequest
from backend.api.schemas.currency import ShowCurrency
from backend.api.schemas.tag import ShowTag
from backend.api.schemas.transaction import ShowTransaction, ShowTransactionType, OrderBy
from backend.db.dals import AccountDAL, CurrencyDAL
from backend.db.session import get_db
from backend.exception import AccountNotFound, TransactionTypeNotFound


router = APIRouter(
    prefix="/account"
)


async def _create_new_account(request_body: AccountCreate, db) -> CreatedAccountResponse:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)

            account = await account_dal.create_account(
                name=request_body.name,
                balance=request_body.balance,
                currency_id=request_body.currency_id
            )

            return CreatedAccountResponse(created_account_id=account.id)


async def _get_account_by_id(account_id: uuid.UUID, db) -> ShowAccount:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)

            account = await account_dal.get_account_by_id(
                account_id=account_id
            )

            currency_dal = CurrencyDAL(session)

            currency = await currency_dal.get_currency_by_id(account.currency_id)

            return ShowAccount(
                id=account.id,
                balance=account.balance,
                currency=ShowCurrency(
                    id=currency.id,
                    name=currency.name
                ),
                name=account.name,
                created_at=account.created_at,
            )


async def _update_account(
        account_id: uuid.UUID, updated_account_params: dict, db
) -> UpdatedAccountResponse:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            updated_account_id = await account_dal.update_account(
                account_id=account_id,
                **updated_account_params
            )
            return UpdatedAccountResponse(updated_account_id=updated_account_id)


async def _delete_account(account_id: uuid.UUID, db) -> DeletedAccountResponse:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            deleted_account_id = await account_dal.delete_account(
                account_id=account_id,
            )
            return DeletedAccountResponse(deleted_account_id=deleted_account_id)


async def _get_account_transactions(
        account_id: uuid.UUID,
        db,
        transaction_type_id: int | None = None,
        tag_id: uuid.UUID | None = None,
        order_by: OrderBy = OrderBy("id")
) -> Sequence[ShowTransaction] | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            account_transactions = await account_dal.get_account_transactions(
                account_id=account_id,
                transaction_type_id=transaction_type_id,
                tag_id=tag_id,
                order_by=order_by
            )

            return tuple(ShowTransaction(
                id=transaction.id,
                transaction_type=ShowTransactionType(
                    id=transaction_type.id,
                    name=transaction_type.name
                ),
                amount=transaction.amount,
                tag=ShowTag(
                    id=tag.id,
                    name=tag.name
                ) if tag_id is not None else None,
                account=ShowAccount(
                    id=account.id,
                    name=account.name,
                    balance=account.balance,
                    currency=ShowCurrency(
                        id=currency.id,
                        name=currency.name,
                    ),
                    created_at=account.created_at,
                ),
                created_at=transaction.created_at
            ) for transaction, account, tag, transaction_type, currency in account_transactions)


@router.post("/")
async def create_account(
        request_body: AccountCreate, db: AsyncSession = Depends(get_db)
) -> CreatedAccountResponse:
    return await _create_new_account(request_body, db)


@router.get("/", response_model=ShowAccount)
async def get_account(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowAccount:
    try:
        account = await _get_account_by_id(account_id, db)
    except AccountNotFound as exception:
        raise exception
    return account


@router.patch("/", response_model=UpdatedAccountResponse)
async def update_account(
        account_id: uuid.UUID, request_body: UpdateAccountRequest,
        db: AsyncSession = Depends(get_db)
) -> UpdatedAccountResponse:

    updated_account_params = request_body.dict(exclude_none=True)
    if len(updated_account_params) == 0:
        raise HTTPException(
            status_code=422,
            detail=f"At least 1 parameter for account update should be provided"
        )
    try:
        updated_account_response = await _update_account(
            account_id=account_id,
            updated_account_params=updated_account_params,
            db=db
        )
    except AccountNotFound as exception:
        raise exception

    return updated_account_response


@router.delete("/", response_model=DeletedAccountResponse)
async def delete_account(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DeletedAccountResponse:
    try:
        deleted_account_response = await _delete_account(
            account_id=account_id,
            db=db
        )
    except AccountNotFound as exception:
        raise exception

    return deleted_account_response


@router.get("/transactions/")
async def get_account_transactions(
        request_body: GetAccountTransactionsRequest, db: AsyncSession = Depends(get_db)
) -> Sequence[ShowTransaction]:
    print(request_body)
    try:
        account_transactions = await _get_account_transactions(
            account_id=request_body.account_id,
            db=db,
            transaction_type_id=request_body.transaction_type_id,
            tag_id=request_body.tag_id,
            order_by=request_body.order_by
        )
    except (AccountNotFound, TransactionTypeNotFound) as exception:
        raise exception
    
    return account_transactions
