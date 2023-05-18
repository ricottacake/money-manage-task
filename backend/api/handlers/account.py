import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import AccountCreate, ShowAccount, \
    UpdateAccountRequest, UpdatedAccountResponse, DeletedAccountResponse, CreatedAccountResponse
from backend.api.schemas.transaction import ShowTransaction
from backend.db.dals import AccountDAL
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

            return ShowAccount(
                id=account.id,
                balance=account.balance,
                currency_id=account.currency_id,
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
        tag_id: uuid.UUID | None = None
) -> Sequence[ShowTransaction] | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            account_transactions = await account_dal.get_account_transactions(
                account_id=account_id,
                transaction_type_id=transaction_type_id,
                tag_id=tag_id
            )

            return tuple(ShowTransaction(
                id=transaction.id,
                transaction_type_id=transaction.transaction_type_id,
                amount=transaction.amount,
                tag_id=transaction.tag_id,
                account_id=transaction.account_id,
                created_at=transaction.created_at
            ) for transaction in account_transactions)


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
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db),
        transaction_type_id: int | None = None,
        tag_id: uuid.UUID | None = None
) -> Sequence[ShowTransaction]:
    try:
        account_transactions = await _get_account_transactions(
            account_id=account_id,
            db=db,
            transaction_type_id=transaction_type_id,
            tag_id=tag_id
        )
    except (AccountNotFound, TransactionTypeNotFound) as exception:
        raise exception

    return account_transactions
