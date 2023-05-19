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


async def get_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()

