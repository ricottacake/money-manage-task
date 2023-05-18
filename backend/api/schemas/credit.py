import uuid

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel


class ShowCredit(TunedModel):
    id: uuid.UUID
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class CreateCredit(BaseModel):
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class UpdateCreditRequest(BaseModel):
    amount: float | None = Field(.0, ge=0, lt=10 ** 10)
    account_id: uuid.UUID | None


class UpdatedCreditResponse(BaseModel):
    updated_credit_id: uuid.UUID


class DeletedCreditResponse(BaseModel):
    deleted_credit_id: uuid.UUID
