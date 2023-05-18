import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.transaction import TransactionCreate, ShowTransaction, \
    UpdateTransactionRequest, UpdatedTransactionResponse, DeletedTransactionResponse, \
    ShowTransactionType, CreatedTransactionResponse
from backend.db.dals import TransactionDAL
from backend.db.session import get_db, TransactionTypeEnum
from backend.exception import TransactionNotFound, TransactionTypeNotFound, TagNotFound, \
    AccountNotFound

router = APIRouter(
    prefix="/transaction"
)


async def _create_new_transaction(
        request_body: TransactionCreate, db
) -> CreatedTransactionResponse:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.create_transaction(
                transaction_type_id=request_body.transaction_type_id,
                amount=request_body.amount,
                account_id=request_body.account_id,
                tag_id=request_body.tag_id
            )

            return CreatedTransactionResponse(created_transaction_id=transaction.id)


async def _get_transaction_by_id(transaction_id: uuid.UUID, db) -> ShowTransaction:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.get_transaction_by_id(
                transaction_id=transaction_id
            )

            return ShowTransaction(
                id=transaction.id,
                transaction_type_id=transaction.transaction_type_id,
                amount=transaction.amount,
                tag_id=transaction.tag_id,
                account_id=transaction.account_id,
                created_at=transaction.created_at
            )


async def _get_transaction_type_by_id(transaction_type_id: int, db) -> ShowTransactionType:
    async with db as session:
        async with session.begin():
            try:
                transaction_type_enum = TransactionTypeEnum(transaction_type_id)
            except ValueError:
                raise TransactionTypeNotFound(transaction_type_id=transaction_type_id)

            return ShowTransactionType(
                id=transaction_type_enum.value,
                name=transaction_type_enum.name
            )


async def _get_transactions(
        db, transaction_type_id: int | None = None, tag_id: uuid.UUID | None = None
                            ) -> Sequence[ShowTransaction]:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)
            transactions = await transaction_dal.get_transactions(
                transaction_type_id=transaction_type_id, tag_id=tag_id
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
) -> UpdatedTransactionResponse:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)
            updated_transaction_id = await transaction_dal.update_transaction(
                transaction_id=transaction_id,
                **updated_transaction_params
            )
            return UpdatedTransactionResponse(updated_transaction_id=updated_transaction_id)


async def _delete_transaction(transaction_id: uuid.UUID, db) -> DeletedTransactionResponse:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)
            deleted_transaction_id = await transaction_dal.delete_transaction(
                transaction_id=transaction_id,
            )
            return DeletedTransactionResponse(deleted_transaction_id=deleted_transaction_id)


@router.post("/")
async def create_transaction(
        request_body: TransactionCreate, db: AsyncSession = Depends(get_db)
) -> CreatedTransactionResponse:
    try:
        created_transaction_response = await _create_new_transaction(request_body, db)
    except (
            AccountNotFound, TransactionNotFound, TransactionTypeNotFound, TagNotFound
    ) as exception:
        raise exception

    return created_transaction_response


@router.get("/", response_model=ShowTransaction)
async def get_transaction(
        transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowTransaction:
    try:
        transaction = await _get_transaction_by_id(transaction_id, db)
    except TransactionNotFound as exception:
        raise exception
    return transaction


@router.patch("/", response_model=UpdatedTransactionResponse)
async def update_transaction(
        transaction_id: uuid.UUID, request_body: UpdateTransactionRequest,
        db: AsyncSession = Depends(get_db)
) -> UpdatedTransactionResponse:
    updated_transaction_params = request_body.dict(exclude_none=True)
    if len(updated_transaction_params) == 0:
        raise HTTPException(
            status_code=422,
            detail=f"At least 1 parameter for transaction update should be provided"
        )

    try:
        updated_transaction_response = await _update_transaction(
            transaction_id=transaction_id,
            updated_transaction_params=updated_transaction_params,
            db=db
        )
    except TransactionNotFound as expection:
        raise expection

    return updated_transaction_response


@router.delete("/", response_model=DeletedTransactionResponse)
async def delete_transaction(
        transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DeletedTransactionResponse:
    try:
        deleted_transaction_response = await _delete_transaction(
            transaction_id=transaction_id,
            db=db
        )
    except TransactionNotFound as exception:
        raise exception

    return deleted_transaction_response


@router.get("/type/", response_model=ShowTransactionType)
async def get_transaction_type(
        transaction_type_id: int, db: AsyncSession = Depends(get_db)
) -> ShowTransactionType:
    try:
        transaction_type = await _get_transaction_type_by_id(transaction_type_id, db)
    except TransactionTypeNotFound as exception:
        raise exception

    return transaction_type


@router.get("/all/")
async def get_transactions(
        db: AsyncSession = Depends(get_db),
        transaction_type_id: int | None = None,
        tag_id: uuid.UUID | None = None
) -> Sequence[ShowTransaction]:
    try:
        transactions = await _get_transactions(
            db=db, transaction_type_id=transaction_type_id, tag_id=tag_id
        )
    except TransactionNotFound as exception:
        raise exception

    return transactions
