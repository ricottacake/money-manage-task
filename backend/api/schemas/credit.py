import uuid

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel
from backend.api.schemas.account import ShowAccount


class ShowCredit(TunedModel):
    id: uuid.UUID
    name: str
    amount: float
    account: ShowAccount
    is_open: bool


class CreateCreditRequest(BaseModel):
    name: str
    amount: float = Field(1000, gt=0, lt=10**10)
    account_id: uuid.UUID
    tag_id: uuid.UUID | None


class CreatedCreditResponse(BaseModel):
    created_credit_id: uuid.UUID
    created_credit_transaction_id: uuid.UUID


class CloseCreditRequest(BaseModel):
    credit_id: uuid.UUID


class ClosedCreditResponse(BaseModel):
    closed_credit_id: uuid.UUID
    created_credit_transaction_id: uuid.UUID


class UpdateCreditRequest(BaseModel):
    name: str


class UpdatedCreditResponse(BaseModel):
    updated_credit_id: uuid.UUID


class DeletedCreditResponse(BaseModel):
    deleted_credit_id: uuid.UUID
