from collections.abc import Generator
from enum import Enum

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, create_session
from sqlalchemy import create_engine

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


TRANSACTION_TYPE_DATA = (
    {"id": 1, "name": "income"},
    {"id": 2, "name": "expense"},
    {"id": 3, "name": "money_transfer_sender"},
    {"id": 4, "name": "money_transfer_receiver"},
)


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


def _db_pre_session():
    from backend.db.models import TransactionType, Currency

    sync_db_url = db_url[:10] + db_url[18:]
    sync_engine = create_engine(sync_db_url)

    is_updated = False

    with create_session(sync_engine) as db_session:
        for transaction_type_data in TRANSACTION_TYPE_DATA:
            transaction_type = db_session.get(TransactionType, transaction_type_data["id"])
            if transaction_type is None:
                db_session.add(TransactionType(**transaction_type_data))
                is_updated = True
            elif transaction_type.name != transaction_type_data["name"]:
                raise ValueError(
                    "TransactionType with id {id} does not '{name}'!".format(**transaction_type_data)
                )

        if db_session.query(TransactionType).count() != 4:
            raise ValueError("Too many TransactionType rows. There should be only 4 of them!")

        for currency_data in CURRENCY_DATA:
            currency = db_session.get(Currency, currency_data["id"])
            if currency is None:
                db_session.add(Currency(**currency_data))
                is_updated = True
            elif currency.name != currency_data["name"]:
                raise ValueError(
                    "Currency with id {id} does not '{name}'!".format(**currency_data)
                )

        if is_updated:
            db_session.flush()
            db_session.commit()

        print("This run here")


async def get_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()

_db_pre_session()
