import uuid
from datetime import datetime

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel, OrderBy
from backend.api.schemas.account import ShowAccount
from backend.api.schemas.tag import ShowTag


class ShowTransactionType(TunedModel):
    id: int
    name: str


class TransactionTypeCreate(BaseModel):
    name: str


class ShowTransaction(TunedModel):
    id: uuid.UUID
    transaction_type: ShowTransactionType
    amount: float
    tag: ShowTag | None
    account: ShowAccount
    created_at: datetime


class TransactionCreate(BaseModel):
    transaction_type_id: int
    amount: float = Field(.0, ge=0, lt=10**10)
    tag_id: uuid.UUID | None
    account_id: uuid.UUID


class CreatedTransactionResponse(BaseModel):
    created_transaction_id: uuid.UUID


class UpdateTransactionRequest(BaseModel):
    transaction_type_id: int | None
    amount: float | None
    tag_id: uuid.UUID | None


class GetTransactionsRequest(BaseModel):
    transaction_type_id: int | None
    tag_id: uuid.UUID | None
    order_by: OrderBy


class UpdatedTransactionResponse(BaseModel):
    updated_transaction_id: uuid.UUID


class DeletedTransactionResponse(BaseModel):
    deleted_transaction_id: uuid.UUID
