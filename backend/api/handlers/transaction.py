import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.transaction import TransactionCreate, ShowTransaction, \
    UpdateTransactionRequest, UpdatedTransactionResponse, DeletedTransactionResponse, \
    ShowTransactionType, CreatedTransactionResponse
from backend.db.dals import TransactionDAL, TransactionTypeDAL, AccountDAL
from backend.db.session import get_db


router = APIRouter(
    prefix="/transaction"
)


async def _create_new_transaction(body: TransactionCreate, db) -> uuid.UUID | None:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.create_transaction(
                transaction_type_id=body.transaction_type_id,
                amount=body.amount,
                account_id=body.account_id,
                tag_id=body.tag_id
            )

            if transaction is not None:
                return transaction.id


async def _get_transaction_by_id(transaction_id: uuid.UUID, db) -> ShowTransaction | None:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.get_transaction_by_id(
                transaction_id=transaction_id
            )

            if transaction is not None:
                return ShowTransaction(
                    id=transaction.id,
                    transaction_type_id=transaction.transaction_type_id,
                    amount=transaction.amount,
                    tag_id=transaction.tag_id,
                    account_id=transaction.account_id,
                    created_at=transaction.created_at
                )


async def _get_transaction_type_by_id(transaction_type_id: int, db) -> ShowTransactionType | None:
    async with db as session:
        async with session.begin():
            transaction_type_dal = TransactionTypeDAL(session)

            transaction_type = await transaction_type_dal.get_transaction_type_by_id(
                transaction_type_id=transaction_type_id
            )

            if transaction_type is not None:
                return ShowTransactionType(
                    id=transaction_type.id,
                    name=transaction_type.name
                )


async def _get_transactions(db, transaction_type_id: int | None = None
                            ) -> Sequence[ShowTransaction] | None:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            if transaction_type_id is not None:
                transaction_type_dal = TransactionTypeDAL(session)
                transaction_type = await transaction_type_dal.get_transaction_type_by_id(
                    transaction_type_id
                )
                if transaction_type is None:
                    return

            transactions = await transaction_dal.get_transactions(
                transaction_type_id=transaction_type_id
            )

            return tuple(ShowTransaction(
                id=transaction.id,
                transaction_type_id=transaction.transaction_type_id,
                amount=transaction.amount,
                tag_id=transaction.tag_id,
                account_id=transaction.account_id,
                created_at=transaction.created_at
            ) for transaction in transactions)


async def _update_transaction(
        transaction_id: uuid.UUID, updated_transaction_params: dict, db
) -> uuid.UUID | None:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)
            updated_transaction_id = await transaction_dal.update_transaction(
                transaction_id=transaction_id,
                **updated_transaction_params
            )
            return updated_transaction_id


async def _delete_transaction(transaction_id: uuid.UUID, db) -> uuid.UUID | None:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)
            deleted_transaction_id = await transaction_dal.delete_transaction(
                transaction_id=transaction_id,
            )
            return deleted_transaction_id


@router.post("/")
async def create_transaction(
        body: TransactionCreate, db: AsyncSession = Depends(get_db)
) -> CreatedTransactionResponse:
    created_transaction_id = await _create_new_transaction(body, db)

    if created_transaction_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not found Transaction or Tag or Account by id"
        )
    return CreatedTransactionResponse(created_transaction_id=created_transaction_id)


@router.get("/", response_model=ShowTransaction)
async def get_transaction(
        transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowTransaction:
    transaction = await _get_transaction_by_id(transaction_id, db)
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with id {transaction_id} not found."
        )
    return transaction


@router.patch("/", response_model=UpdatedTransactionResponse)
async def update_transaction(
        transaction_id: uuid.UUID, body: UpdateTransactionRequest,
        db: AsyncSession = Depends(get_db)
) -> UpdatedTransactionResponse:
    updated_transaction_params = body.dict(exclude_none=True)
    if updated_transaction_params == {}:
        raise HTTPException(
            status_code=422,
            detail=f"At least 1 parameter for transaction update should be provided"
        )

    updated_transaction_id = await _update_transaction(
        transaction_id=transaction_id,
        updated_transaction_params=updated_transaction_params,
        db=db
    )

    if updated_transaction_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with id {transaction_id} not found."
        )

    return UpdatedTransactionResponse(updated_transaction_id=updated_transaction_id)


@router.delete("/", response_model=DeletedTransactionResponse)
async def delete_transaction(
        transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DeletedTransactionResponse:
    deleted_transaction_id = await _delete_transaction(
        transaction_id=transaction_id,
        db=db
    )

    if deleted_transaction_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with id {transaction_id} not found."
        )

    return DeletedTransactionResponse(deleted_transaction_id=deleted_transaction_id)


@router.get("/type/", response_model=ShowTransactionType)
async def get_transaction_type(
        transaction_type_id: int, db: AsyncSession = Depends(get_db)
) -> ShowTransactionType:
    transaction_type = await _get_transaction_type_by_id(transaction_type_id, db)
    if transaction_type is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction type with id {transaction_type_id} not found."
        )
    return transaction_type


@router.get("/all/")
async def get_transactions(
        db: AsyncSession = Depends(get_db), transaction_type_id: int | None = None
) -> Sequence[ShowTransaction]:
    transactions = await _get_transactions(
        db=db, transaction_type_id=transaction_type_id
    )

    if transactions is None:
        raise HTTPException(
            status_code=404,
            detail=f"TransactionType id not found."
        )

    return transactions
