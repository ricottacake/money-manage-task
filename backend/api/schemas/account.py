import uuid
from datetime import datetime

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel


class ShowAccount(TunedModel):
    id: uuid.UUID
    name: str
    balance: float
    currency_id: int
    created_at: datetime


class AccountCreate(BaseModel):
    id: uuid.UUID
    name: str
    balance: float = Field(.0, ge=0, lt=10**10)
    currency_id: int
    created_at: datetime


class UpdateAccountRequest(BaseModel):
    name: str | None
    balance: float | None
    currency_id: int | None


class UpdatedAccountResponse(BaseModel):
    updated_account_id: uuid.UUID


class DeletedAccountResponse(BaseModel):
    deleted_account_id: uuid.UUID
