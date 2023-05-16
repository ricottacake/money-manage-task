import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Transaction, Account, TransactionType, Currency, Tag


# DAL - Data Access Layer
class TransactionDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_transaction(
            self, transaction_type_id: int, amount: float, account_id: uuid.UUID,
            tag_id: uuid.UUID | None = None
    ) -> Transaction:

        new_transaction = Transaction(
            transaction_type_id=transaction_type_id,
            amount=amount,
            account_id=account_id,
            tag_id=tag_id
        )

        self.db_session.add(new_transaction)
        await self.db_session.flush()
        return new_transaction

    async def get_transaction(self, transaction_id: uuid.UUID) -> Transaction:
        return await self.db_session.get(Transaction, transaction_id)

    async def update_transaction(self, transaction_id: uuid.UUID, **kwargs) -> Transaction:
        transaction = await self.get_transaction(transaction_id)

        for key, value in kwargs.items():
            if key in transaction:
                transaction[key] = value

        await self.db_session.flush()
        return transaction


class AccountDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_account(self, account_id: uuid.UUID) -> Account:
        return await self.db_session.get(Account, account_id)


class TransactionTypeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_transaction_type(self, transaction_type_id: int) -> TransactionType:
        return await self.db_session.get(TransactionType, transaction_type_id)


class CurrencyDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_currency(self, currency_id: int) -> Currency:
        return await self.db_session.get(Currency, currency_id)


class TagDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_tag(self, tag_id: uuid.UUID) -> Tag:
        return await self.db_session.get(Tag, tag_id)
