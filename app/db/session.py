import enum
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, create_session
from sqlalchemy import create_engine

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


@enum.unique
class TransactionTypeEnum(enum.IntEnum):
    income = 1
    expense = 2
    money_transfer_sender = 3
    money_transfer_receiver = 4
    credit_open = 5
    credit_close = 6
    deposit_open = 7
    deposit_close = 8

    @property
    def is_plus_sign(self) -> bool:
        return self.name in ("income", "money_transfer_receiver", "credit_open", "deposit_close")

    @property
    def is_reserved_type(self) -> bool:
        return self.name not in ("income", "expense")


CURRENCY_DATA = (
    {"id": 1, "name": "uah"},
    {"id": 2, "name": "usd"},
)

db_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(db_url, future=True, echo=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def _compare_transaction_type_enum_with_db_table(_db_session):
    from app.db.models import TransactionType

    for transaction_type in TransactionTypeEnum:
        transaction_type_name, transaction_type_id = transaction_type.name, transaction_type.value
        transaction_type = await _db_session.get(TransactionType, transaction_type_id)
        if transaction_type is None:
            await _db_session.add(
                TransactionType(
                    id=transaction_type_id,
                    name=transaction_type_name
                )
            )
        elif transaction_type.name != transaction_type_name:
            raise ValueError(
                f"TransactionType with id '{transaction_type_id}' "
                f"does not '{transaction_type_name}'!"
            )

    await _db_session.flush()

    if await _db_session.query(TransactionType).count() != len(TransactionTypeEnum):
        raise ValueError(f"Too many TransactionType rows. "
                         f"There should be only {len(TransactionTypeEnum)} of them!")


async def _autofill_currency_db_table(_db_session):
    from app.db.models import Currency

    for currency_data in CURRENCY_DATA:
        currency = await _db_session.get(Currency, currency_data["id"])
        if currency is None:
            await _db_session.add(Currency(**currency_data))
        elif currency.name != currency_data["name"]:
            raise ValueError(
                "Currency with id {id} does not '{name}'!".format(**currency_data)
            )


async def db_pre_session():
    async with Depends(get_db) as session:
        async with session.begin() as db_session:
            await _compare_transaction_type_enum_with_db_table(db_session)
            await _autofill_currency_db_table(db_session)

            await db_session.flush()
            await db_session.commit()


async def get_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()

db_pre_session()
