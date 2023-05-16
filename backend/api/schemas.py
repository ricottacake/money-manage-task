import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class ShowTag(TunedModel):
    id: uuid.UUID
    name: str


class TagCreate(BaseModel):
    name: str


class ShowCurrency(TunedModel):
    id: int
    name: str


class CurrencyCreate(BaseModel):
    name: str


class ShowAccount(TunedModel):
    id: uuid.UUID
    name: str
    balance: float = Field(.0, ge=0, lt=10**10)
    currency: ShowCurrency
    created_at: datetime


class AccountCreate(BaseModel):
    id: uuid.UUID
    name: str
    balance: float = Field(.0, ge=0, lt=10**10)
    currency_id: int
    created_at: datetime


class ShowTransactionType(TunedModel):
    id: int
    name: str


class TransactionTypeCreate(BaseModel):
    name: str


class ShowCredit(TunedModel):
    id: uuid.UUID
    amount: float = Field(.0, ge=0, lt=10**10)
    account: ShowAccount


class CreateCredit(BaseModel):
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class ShowDeposit(TunedModel):
    id: uuid.UUID
    amount: float = Field(.0, ge=0, lt=10**10)
    account: ShowAccount


class DepositCreate(BaseModel):
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class ShowTransaction(TunedModel):
    id: uuid.UUID
    transaction_type: ShowTransactionType
    amount: float = Field(.0, ge=0, lt=10**10)
    tag: ShowTag
    account: ShowAccount
    created_at: datetime


class TransactionCreate(BaseModel):
    transaction_type_id: int
    amount: float = Field(.0, ge=0, lt=10**10)
    tag_id: uuid.UUID
    account_id: uuid.UUID
