import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.account import AccountCreate, ShowAccount, \
    UpdateAccountRequest, UpdatedAccountResponse, DeletedAccountResponse
from backend.db.dals import AccountDAL
from backend.db.session import get_db


router = APIRouter(
    prefix="/account"
)


async def _create_new_account(body: AccountCreate, db) -> uuid.UUID:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)

            account = await account_dal.create_account(
                name=body.name,
                balance=body.balance,
                currency_id=body.currency_id
            )

            return account.id


async def _get_account_by_id(account_id: uuid.UUID, db) -> ShowAccount | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)

            account = await account_dal.get_account_by_id(
                account_id=account_id
            )

            if account is not None:
                return ShowAccount(
                    id=account.id,
                    balance=account.balance,
                    currency_id=account.currency_id,
                    name=account.name,
                    created_at=account.created_at,
                )


async def _update_account(
        account_id: uuid.UUID, updated_account_params: dict, db
) -> uuid.UUID | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            updated_account_id = await account_dal.update_account(
                account_id=account_id,
                **updated_account_params
            )
            return updated_account_id


async def _delete_account(account_id: uuid.UUID, db) -> uuid.UUID | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            deleted_account_id = await account_dal.delete_account(
                account_id=account_id,
            )
            return deleted_account_id


@router.post("/")
async def create_account(
        body: AccountCreate, db: AsyncSession = Depends(get_db)
) -> uuid.UUID:
    return await _create_new_account(body, db)


@router.get("/", response_model=ShowAccount)
async def get_account(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowAccount:
    account = await _get_account_by_id(account_id, db)
    if account is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account with id {account_id} not found."
        )
    return account


@router.patch("/", response_model=UpdatedAccountResponse)
async def update_account(
        account_id: uuid.UUID, body: UpdateAccountRequest,
        db: AsyncSession = Depends(get_db)
) -> UpdatedAccountResponse:
    print(body)
    updated_account_params = body.dict(exclude_none=True)
    if updated_account_params == {}:
        raise HTTPException(
            status_code=422,
            detail=f"At least 1 parameter for account update should be provided"
        )
    print(updated_account_params)
    updated_account_id = await _update_account(
        account_id=account_id,
        updated_account_params=updated_account_params,
        db=db
    )

    if updated_account_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account with id {account_id} not found."
        )

    return UpdatedAccountResponse(updated_account_id=updated_account_id)


@router.delete("/", response_model=DeletedAccountResponse)
async def delete_account(
        account_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DeletedAccountResponse:
    deleted_account_id = await _delete_account(
        account_id=account_id,
        db=db
    )

    if deleted_account_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account with id {account_id} not found."
        )

    return DeletedAccountResponse(deleted_account_id=deleted_account_id)
