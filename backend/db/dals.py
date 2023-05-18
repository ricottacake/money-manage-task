import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import select, update, delete, Row, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.transaction import OrderBy
from backend.db.models import TransactionType as TrType, Transaction, \
    Account, Currency, Tag, Deposit, Credit


# DAL - Data Access Layer
from backend.db.session import TransactionTypeEnum
from backend.exception import AccountNotFound, TransactionTypeNotFound, TransactionNotFound, \
    TagNotFound, CurrencyNotFound, TransferTransactionChange


class BaseDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class UserDAL(BaseDAL):
    async def get_accounts(self) -> Sequence[Row]:
        query = select(Account, Currency).join(Currency, Account.currency_id == Currency.id, isouter=True)
        query_result = await self.db_session.execute(query)
        return query_result.fetchall()


class TransactionDAL(BaseDAL):
    async def create_transaction(
            self,
            transaction_type_id: int,
            amount: float,
            account_id: uuid.UUID,
            tag_id: uuid.UUID | None = None,
            created_at: datetime | None = None
    ) -> Transaction:

        if tag_id is not None:
            tag_dal = TagDAL(self.db_session)
            await tag_dal.check_if_tag_exists(tag_id)

        is_positive_transaction = TransactionTypeEnum(transaction_type_id).is_plus_sign
        # if it is income -> add, expense -> subtract
        sign = 2*is_positive_transaction - 1

        account_dal = AccountDAL(self.db_session)
        checkpoint = self.db_session.begin_nested()
        try:
            await account_dal.add_to_balance(account_id, amount=amount*sign)

            new_transaction = Transaction(
                transaction_type_id=transaction_type_id,
                amount=amount,
                account_id=account_id,
                tag_id=tag_id,
                created_at=datetime.utcnow() if created_at is None else created_at
            )
        except AccountNotFound as exception:
            raise exception
        except Exception as exception:
            await checkpoint.rollback()
            raise exception

        self.db_session.add(new_transaction)
        await self.db_session.flush()
        return new_transaction

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Transaction:
        transaction = await self.db_session.get(Transaction, transaction_id)
        if transaction is None:
            raise TransactionNotFound(transaction_id=transaction_id)
        return transaction

    async def update_transaction(self, transaction_id: uuid.UUID, **kwargs) -> Transaction:
        transaction = await self.get_transaction_by_id(transaction_id=transaction_id)
        if TransactionTypeEnum(transaction.transaction_type_id).is_transfer_type:
            raise TransferTransactionChange

        if TransactionTypeEnum(kwargs.get("transaction_type_id", 1)).is_transfer_type:
            raise TransferTransactionChange

        if "amount" not in kwargs and "transaction_type_id" not in kwargs:
            query = update(Transaction) \
                .where(Transaction.id == transaction_id) \
                .values(**kwargs) \
                .returning(Transaction.id)
            query_result = await self.db_session.execute(query)

            update_transaction_id_row = query_result.fetchone()

            return update_transaction_id_row[0]

        was_positive_transaction = TransactionTypeEnum(transaction.transaction_type_id).is_plus_sign
        old_sign = 2 * was_positive_transaction - 1
        old_amount = transaction.amount

        new_transaction_type_id = kwargs.get("transaction_type_id", transaction.transaction_type_id)
        is_positive_transaction = TransactionTypeEnum(new_transaction_type_id).is_plus_sign
        new_sign = 2 * is_positive_transaction - 1
        new_amount = kwargs.get("amount", old_amount)

        diff_amount = -old_sign * old_amount + new_sign * new_amount

        account_dal = AccountDAL(self.db_session)
        checkpoint = self.db_session.begin_nested()
        try:
            await account_dal.add_to_balance(transaction.account_id, diff_amount)

            query = update(Transaction)\
                .where(Transaction.id == transaction_id)\
                .values(**kwargs)\
                .returning(Transaction.id)
            query_result = await self.db_session.execute(query)

        except AccountNotFound as exception:
            raise exception
        except Exception as exception:
            await checkpoint.rollback()
            raise exception

        update_transaction_id_row = query_result.fetchone()

        return update_transaction_id_row[0]

    async def delete_transaction(self, transaction_id: uuid.UUID) -> uuid.UUID:
        transaction = await self.get_transaction_by_id(transaction_id=transaction_id)
        if TransactionTypeEnum(transaction.transaction_type_id).is_transfer_type:
            raise TransferTransactionChange

        is_positive_transaction = TransactionTypeEnum(transaction.transaction_type_id).is_plus_sign
        sign = 2 * is_positive_transaction - 1

        account_dal = AccountDAL(self.db_session)
        checkpoint = self.db_session.begin_nested()
        try:
            await account_dal.add_to_balance(
                transaction.account_id,
                amount=transaction.amount * -sign
            )

            query = delete(Transaction)\
                .where(Transaction.id == transaction_id)\
                .returning(Transaction.id)
            query_result = await self.db_session.execute(query)

        except AccountNotFound as exception:
            raise exception
        except Exception as exception:
            await checkpoint.rollback()
            raise exception

        delete_transaction_id_row = query_result.fetchone()

        return delete_transaction_id_row[0]

    async def get_transactions(
            self, account_id: uuid.UUID | None = None,
            transaction_type_id: int | None = None,
            tag_id: uuid.UUID | None = None,
            order_by: OrderBy = OrderBy("id")
    ) -> Sequence[Row] | None:
        query = select(Transaction, Account, Tag, TrType, Currency)
        if account_id is not None:
            account_dal = AccountDAL(self.db_session)
            await account_dal.check_if_account_exists(account_id=account_id)

            query = query.where(Transaction.account_id == account_id)

        if transaction_type_id is not None:
            if transaction_type_id not in map(lambda x: x.value, TransactionTypeEnum):
                raise TransactionTypeNotFound(transaction_type_id=transaction_type_id)

            query = query.filter(Transaction.transaction_type_id == transaction_type_id)

        if tag_id is not None:
            await TagDAL(self.db_session).check_if_tag_exists(tag_id=tag_id)
            query = query.filter(Transaction.tag_id == tag_id)

        query = query.join(Account, Transaction.account_id == Account.id, isouter=True)\
            .join(Tag, Transaction.tag_id == Tag.id, isouter=True)\
            .join(TrType, Transaction.transaction_type_id == TrType.id, isouter=True)\
            .join(Currency, Account.currency_id == Currency.id, isouter=True)

        if order_by == order_by.chronological:
            query = query.order_by(Transaction.created_at)
        elif order_by == order_by.reverse_chronological:
            query = query.order_by(desc(Transaction.created_at))

        query_result = await self.db_session.execute(query)
        return query_result.fetchall()


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

    async def get_account_by_id(self, account_id: uuid.UUID) -> Account:
        account = await self.db_session.get(Account, account_id)
        if account is None:
            raise AccountNotFound(account_id=account_id)
        return account

    async def update_account(self, account_id: uuid.UUID, **kwargs) -> Account:
        query = update(Account) \
            .filter(Account.id == account_id) \
            .values(**kwargs) \
            .returning(Account.id)

        query_result = await self.db_session.execute(query)
        updated_account_id_row = query_result.fetchone()

        if updated_account_id_row is None:
            raise AccountNotFound(account_id=account_id)

        return updated_account_id_row[0]

    async def delete_account(self, account_id: uuid.UUID) -> uuid.UUID | None:
        query = delete(Account).where(Account.id == account_id).returning(Account.id)
        query_result = await self.db_session.execute(query)
        delete_account_id_row = query_result.fetchone()

        if delete_account_id_row is None:
            raise AccountNotFound(account_id=account_id)
        return delete_account_id_row[0]

    async def add_to_balance(self, account_id: uuid.UUID, amount: float) -> None:
        account = await self.get_account_by_id(account_id=account_id)

        query = update(Account)\
            .where(Account.id == account_id)\
            .values(
                balance=account.balance+amount
            )

        await self.db_session.execute(query)

    async def get_account_transactions(
            self,
            account_id: uuid.UUID,
            transaction_type_id: int | None = None,
            tag_id: uuid.UUID | None = None,
            order_by: OrderBy = OrderBy("id")
    ) -> Sequence[Row]:
        transaction_dal = TransactionDAL(self.db_session)
        return await transaction_dal.get_transactions(
            account_id=account_id, transaction_type_id=transaction_type_id,
            tag_id=tag_id, order_by=order_by
        )

    async def check_if_account_exists(self, account_id: uuid.UUID) -> None:
        account = await self.db_session.get(Account, account_id)
        if account is None:
            raise AccountNotFound(account_id=account_id)


class CurrencyDAL(BaseDAL):
    async def create_currency(self, name: uuid.UUID) -> Currency:
        new_currency = Currency(name=name)
        self.db_session.add(new_currency)
        await self.db_session.flush()
        return new_currency

    async def get_currency_by_id(self, currency_id: int) -> Currency:
        currency = await self.db_session.get(Currency, currency_id)
        if currency is None:
            raise CurrencyNotFound(currency_id=currency_id)
        return currency


class TagDAL(BaseDAL):
    async def create_tag(self, name: str) -> Tag:
        new_tag = Tag(name=name)
        self.db_session.add(new_tag)
        await self.db_session.flush()
        return new_tag

    async def get_tag_by_id(self, tag_id: uuid.UUID) -> Tag:
        tag = await self.db_session.get(Tag, tag_id)
        if tag is None:
            raise TagNotFound(tag_id)
        return tag

    async def update_tag(self, tag_id: uuid.UUID, name: str) -> Tag:
        query = update(Tag) \
            .filter(Tag.id == tag_id) \
            .values(name=name) \
            .returning(Transaction.id)
        query_result = await self.db_session.execute(query)
        update_tag_id_row = query_result.fetchone()

        if update_tag_id_row is None:
            raise TagNotFound(tag_id=tag_id)

        return update_tag_id_row[0]

    async def delete_tag(self, tag_id: uuid.UUID) -> Tag:
        query = delete(Tag).where(Tag.id == tag_id).returning(Tag.id)
        query_result = await self.db_session.execute(query)
        delete_tag_id_row = query_result.fetchone()

        if delete_tag_id_row is None:
            raise TagNotFound(tag_id=tag_id)
        return delete_tag_id_row[0]

    async def check_if_tag_exists(self, tag_id: uuid.UUID) -> None:
        tag = await self.db_session.get(Tag, tag_id)
        if tag is None:
            raise TagNotFound(tag_id)

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
