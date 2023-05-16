import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas import ShowTransaction, TransactionCreate, ShowTag, \
    ShowTransactionType, ShowAccount, ShowCurrency
from backend.db.dals import TransactionDAL, AccountDAL, TransactionTypeDAL, CurrencyDAL, TagDAL
from backend.db.session import get_db

router = APIRouter(
    prefix="/api"
)


async def _create_new_transaction(body: TransactionCreate, db) -> ShowTransaction:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.create_transaction(
                transaction_type_id=body.transaction_type_id,
                amount=body.amount,
                account_id=body.account_id,
                tag_id=body.tag_id
            )

            return ShowTransaction(
                id=transaction.id,
                transaction_type=_get_transaction_type(transaction.transaction_type_id, db),
                amount=transaction.amount,
                tag=_get_tag(transaction.tag_id, db),
                account=_get_account(transaction.account_id, db),
                created_at=transaction.created_at
            )


async def _get_transaction(transaction_id: uuid.UUID, db) -> ShowTransaction:
    async with db as session:
        async with session.begin():
            transaction_dal = TransactionDAL(session)

            transaction = await transaction_dal.get_transaction(
                transaction_id=transaction_id
            )
            print(_get_transaction_type(transaction.transaction_type_id, db))

        transaction_type = await _get_transaction_type(transaction.transaction_type_id, db)
        tag = await _get_tag(transaction.tag_id, db)
        account = await _get_account(transaction.account_id, db)

        return ShowTransaction(
            id=transaction.id,
            transaction_type=transaction_type,
            amount=transaction.amount,
            tag=tag,
            account=account,
            created_at=transaction.created_at
        )


async def _get_tag(tag_id: uuid.UUID, db) -> ShowTag:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)

            tag = await tag_dal.get_tag(tag_id=tag_id)

            return ShowTag(
                id=tag.id,
                name=tag.name
            )


async def _get_transaction_type(transaction_type_id: id, db) -> ShowTransactionType:
    async with db as session:
        async with session.begin():
            transaction_type_dal = TransactionTypeDAL(session)

            transaction_type = await transaction_type_dal.get_transaction_type(
                transaction_type_id=transaction_type_id
            )

            return ShowTransactionType(
                id=transaction_type.id,
                name=transaction_type.name
            )


async def _get_account(account_id: uuid.UUID, db) -> ShowAccount:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)

            account = await account_dal.get_account(
                account_id=account_id
            )

    currency = await _get_currency(account.currency_id, db)

    return ShowAccount(
        id=account.id,
        name=account.name,
        balance=account.balance,
        currency=currency,
        created_at=account.updated_at
    )


async def _get_currency(currency_id: id, db) -> ShowCurrency:
    async with db as session:
        async with session.begin():
            currency_dal = CurrencyDAL(session)

            currency = await currency_dal.get_currency(
                currency_id=currency_id
            )

            return ShowCurrency(
                id=currency.id,
                name=currency.name
            )


@router.post("/transaction", response_model=ShowTransaction)
async def create_transaction(
        body: TransactionCreate, db: AsyncSession = Depends(get_db)
) -> ShowTransaction:
    return await _create_new_transaction(body, db)


@router.get("/transaction", response_model=ShowTransaction)
async def get_transaction(
        transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ShowTransaction:
    return await _get_transaction(transaction_id, db)
