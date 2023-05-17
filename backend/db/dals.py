import uuid
from typing import Sequence

from sqlalchemy import select, update, delete, and_, Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Transaction, Account, TransactionType, Currency, Tag, Deposit, Credit


# DAL - Data Access Layer
from backend.db.session import TRANSACTION_TYPE_DATA


class BaseDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class UserDAL(BaseDAL):
    async def get_accounts(self) -> Sequence[Account] | None:
        query = select(Account)
        query_result = await self.db_session.execute(query)
        return tuple(map(lambda row: row[0], query_result.fetchall()))


class TransactionDAL(BaseDAL):
    async def create_transaction(
            self,
            transaction_type_id: int,
            amount: float,
            account_id: uuid.UUID,
            tag_id: uuid.UUID | None = None
    ) -> Transaction | None:

        new_transaction = Transaction(
            transaction_type_id=transaction_type_id,
            amount=amount,
            account_id=account_id,
            tag_id=tag_id
        )

        tag_dal = TagDAL(self.db_session)

        if await tag_dal.get_tag_by_id(tag_id) is None:
            return

        transaction_type_dal = TransactionTypeDAL(self.db_session)
        is_positive_transaction = await transaction_type_dal.is_positive_transaction(
            transaction_type_id=transaction_type_id
        )

        if is_positive_transaction is None:
            return

        # if it is income -> add, expense -> subtract
        sign = 2*is_positive_transaction - 1

        account_dal = AccountDAL(self.db_session)
        updated_account_id = await account_dal.add_to_balance(account_id, amount=amount*sign)

        if updated_account_id is None:
            return

        self.db_session.add(new_transaction)
        await self.db_session.flush()
        return new_transaction

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Transaction | None:
        return await self.db_session.get(Transaction, transaction_id)

    async def update_transaction(self, transaction_id: uuid.UUID, **kwargs) -> Transaction | None:
        query = update(Transaction)\
            .where(Transaction.id == transaction_id)\
            .values(**kwargs)\
            .returning(Transaction.id)
        query_result = await self.db_session.execute(query)
        update_transaction_id_row = query_result.fetchone()

        if update_transaction_id_row is not None:
            return update_transaction_id_row[0]

    async def delete_transaction(self, transaction_id: uuid.UUID) -> uuid.UUID | None:
        query = delete(Transaction).where(Transaction.id == transaction_id).returning(Transaction.id)
        query_result = await self.db_session.execute(query)
        delete_transaction_id_row = query_result.fetchone()

        if delete_transaction_id_row is not None:
            return delete_transaction_id_row[0]

    async def get_transactions(
            self, account_id, transaction_type_id: int | None = None
    ) -> Sequence[Transaction] | None:
        query = select(Transaction).where(Transaction.account_id == account_id)
        if transaction_type_id is not None:
            query = query.filter(Transaction.transaction_type_id == transaction_type_id)
        query_result = await self.db_session.execute(query)
        return tuple(map(lambda row: row[0], query_result.fetchall()))


class AccountDAL(BaseDAL):
    async def create_account(self, name: str, balance: float, currency_id: int) -> Account:
        new_account = Account(
            name=name,
            balance=balance,
            currency_id=currency_id,
        )

        self.db_session.add(new_account)
        await self.db_session.flush()
        return new_account

    async def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        return await self.db_session.get(Account, account_id)

    async def update_account(self, account_id: uuid.UUID, **kwargs) -> Account | None:
        query = update(Account) \
            .where(Account.id == account_id) \
            .values(**kwargs) \
            .returning(Account.id)
        query_result = await self.db_session.execute(query)
        update_account_id_row = query_result.fetchone()

        if update_account_id_row is not None:
            return update_account_id_row[0]

    async def delete_account(self, account_id: uuid.UUID) -> uuid.UUID | None:
        query = delete(Account).where(Account.id == account_id).returning(Account.id)
        query_result = await self.db_session.execute(query)
        delete_account_id_row = query_result.fetchone()

        if delete_account_id_row is not None:
            return delete_account_id_row[0]

    async def add_to_balance(self, account_id: uuid.UUID, amount: float) -> uuid.UUID | None:
        query = select(Account.balance).where(Account.id == account_id)
        query_result = await self.db_session.execute(query)
        balance = query_result.scalar_one()

        query = update(Account)\
            .where(Account.id == account_id)\
            .values(
                balance=balance+amount
            ).returning(Account.id)

        query_result = await self.db_session.execute(query)
        account_row = query_result.fetchone()
        if account_row is not None:
            return account_row[0]

    async def get_account_transactions(
            self, account_id: uuid.UUID, transaction_type_id: int | None = None
    ) -> Sequence[Transaction] | None:
        transaction_dal = TransactionDAL(self.db_session)
        return await transaction_dal.get_transactions(
            account_id=account_id, transaction_type_id=transaction_type_id
        )


class TransactionTypeDAL(BaseDAL):
    async def get_transaction_type_by_id(self, transaction_type_id: int) -> TransactionType | None:
        return await self.db_session.get(TransactionType, transaction_type_id)

    async def is_positive_transaction(self, transaction_type_id: int) -> bool | None:
        query = select(TransactionType).where(TransactionType.id == transaction_type_id)
        query_result = await self.db_session.execute(query)
        transaction_type_row = query_result.fetchone()
        if transaction_type_row is not None:

            return transaction_type_row[0].name in (
                TRANSACTION_TYPE_DATA[0]["name"], TRANSACTION_TYPE_DATA[2]["name"]
            )


class CurrencyDAL(BaseDAL):
    async def create_currency(self, name: uuid.UUID) -> Currency:
        new_currency = Currency(name=name)
        self.db_session.add(new_currency)
        await self.db_session.flush()
        return new_currency

    async def get_currency_by_id(self, currency_id: uuid.UUID) -> Currency | None:
        return await self.db_session.get(Currency, currency_id)


class TagDAL(BaseDAL):
    async def create_tag(self, name: uuid.UUID) -> Tag:
        new_tag = Tag(name=name)
        self.db_session.add(new_tag)
        await self.db_session.flush()
        return new_tag

    async def get_tag_by_id(self, tag_id: uuid.UUID) -> Tag | None:
        return await self.db_session.get(Tag, tag_id)

    async def update_tag(self, tag_id: uuid.UUID, name: str) -> Tag | None:
        query = update(Tag) \
            .where(Tag.id == tag_id) \
            .values(name=name) \
            .returning(Transaction.id)
        query_result = await self.db_session.execute(query)
        update_tag_id_row = query_result.fetchone()

        if update_tag_id_row is not None:
            return update_tag_id_row[0]

    async def delete_tag(self, tag_id: uuid.UUID) -> None:
        query = select(Tag).where(Tag.id == tag_id)
        await self.db_session.delete(query)

    async def get_tags(self) -> Sequence[Tag]:
        query = select(Tag)
        query_result = await self.db_session.execute(query)
        return tuple(map(lambda row: row[0], query_result.fetchall()))


class DepositDAL(BaseDAL):
    async def create_deposit(
            self, name: uuid.UUID, amount: float, account_id: uuid.UUID
    ) -> Deposit:
        new_deposit = Deposit(
            name=name,
            amount=amount,
            account_id=account_id
        )
        self.db_session.add(new_deposit)
        await self.db_session.flush()
        return new_deposit

    async def get_deposit_by_id(self, deposit_id: uuid.UUID) -> Deposit | None:
        return await self.db_session.get(Deposit, deposit_id)

    async def update_deposit(self, deposit_id: uuid.UUID, **kwargs) -> Deposit | None:
        query = update(Deposit) \
            .where(Deposit.id == deposit_id) \
            .values(**kwargs) \
            .returning(Deposit.id)
        query_result = await self.db_session.execute(query)
        update_deposit_id_row = query_result.fetchone()

        if update_deposit_id_row is not None:
            return update_deposit_id_row[0]

    async def delete_deposit(self, deposit_id: uuid.UUID) -> None:
        query = select(Deposit).where(Deposit.id == deposit_id)
        await self.db_session.delete(query)


class CreditDAL(BaseDAL):
    async def create_credit(
            self, name: uuid.UUID, amount: float, account_id: uuid.UUID
    ) -> Credit:
        new_credit = Credit(
            name=name,
            amount=amount,
            account_id=account_id
        )
        self.db_session.add(new_credit)
        await self.db_session.flush()
        return new_credit

    async def get_credit_by_id(self, credit_id: uuid.UUID) -> Credit | None:
        return await self.db_session.get(Credit, credit_id)

    async def update_credit(self, credit_id: uuid.UUID, **kwargs) -> Credit | None:
        query = update(Credit) \
            .where(Credit.id == credit_id) \
            .values(**kwargs) \
            .returning(Credit.id)
        query_result = await self.db_session.execute(query)
        update_credit_id_row = query_result.fetchone()

        if update_credit_id_row is not None:
            return update_credit_id_row[0]

    async def delete_credit(self, credit_id: uuid.UUID) -> None:
        query = select(Credit).where(Credit.id == credit_id)
        await self.db_session.delete(query)
