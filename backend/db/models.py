import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Tag(Base):
    __tablename__ = "tag"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Account(Base):
    __tablename__ = "account"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=.0)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class Credit(Base):
    __tablename__ = "credit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=1000)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False)


class Deposit(Base):
    __tablename__ = "deposit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=1000)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False)


class TransactionType(Base):
    __tablename__ = "transaction_type"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type_id = Column(Integer, ForeignKey("transaction_type.id"), nullable=False)
    amount = Column(Float, nullable=False, default=1000)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tag.id"), default=None)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
