import uuid
from datetime import datetime

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel, OrderBy
from backend.api.schemas.currency import ShowCurrency


class ShowAccount(TunedModel):
    id: uuid.UUID
    name: str
    balance: float
    currency: ShowCurrency
    created_at: datetime


class AccountCreate(BaseModel):
    id: uuid.UUID
    name: str
    balance: float = Field(.0, ge=0, lt=10**10)
    currency_id: int
    created_at: datetime


class CreatedAccountResponse(BaseModel):
    created_account_id: uuid.UUID


class UpdateAccountRequest(BaseModel):
    name: str | None
    balance: float | None
    currency_id: int | None


class UpdatedAccountResponse(BaseModel):
    updated_account_id: uuid.UUID


class DeletedAccountResponse(BaseModel):
    deleted_account_id: uuid.UUID


class GetAccountTransactionsRequest(BaseModel):
    account_id: uuid.UUID
    transaction_type_id: int | None
    tag_id: uuid.UUID | None
    order_by: OrderBy
