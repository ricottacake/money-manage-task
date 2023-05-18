import uuid
from datetime import datetime

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel


class ShowTransactionType(TunedModel):
    id: int
    name: str


class TransactionTypeCreate(BaseModel):
    name: str


class ShowTransaction(TunedModel):
    id: uuid.UUID
    transaction_type_id: int
    amount: float = Field(.0, ge=0, lt=10**10)
    tag_id: uuid.UUID
    account_id: uuid.UUID
    created_at: datetime


class TransactionCreate(BaseModel):
    transaction_type_id: int
    amount: float = Field(.0, ge=0, lt=10**10)
    tag_id: uuid.UUID
    account_id: uuid.UUID


class CreatedTransactionResponse(BaseModel):
    created_transaction_id: uuid.UUID


class UpdateTransactionRequest(BaseModel):
    transaction_type_id: int | None
    amount: float | None
    tag_id: uuid.UUID | None
    account_id: uuid.UUID | None


class UpdatedTransactionResponse(BaseModel):
    updated_transaction_id: uuid.UUID


class DeletedTransactionResponse(BaseModel):
    deleted_transaction_id: uuid.UUID
