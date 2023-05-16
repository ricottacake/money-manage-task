import uuid

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel


class ShowDeposit(TunedModel):
    id: uuid.UUID
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class DepositCreate(BaseModel):
    amount: float = Field(.0, ge=0, lt=10**10)
    account_id: uuid.UUID


class UpdateDepositRequest(BaseModel):
    amount: float | None = Field(.0, ge=0, lt=10 ** 10)
    account_id: uuid.UUID | None


class UpdatedDepositResponse(BaseModel):
    updated_deposit_id: uuid.UUID


class DeletedDepositResponse(BaseModel):
    deleted_deposit_id: uuid.UUID
