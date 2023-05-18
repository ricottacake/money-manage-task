import uuid

from pydantic import Field

from backend.api.schemas import BaseModel, TunedModel
from backend.api.schemas.account import ShowAccount


class ShowDeposit(TunedModel):
    id: uuid.UUID
    name: str
    amount: float
    account: ShowAccount
    is_open: bool


class CreateDepositRequest(BaseModel):
    name: str
    amount: float = Field(1000, gt=0, lt=10**10)
    account_id: uuid.UUID
    tag_id: uuid.UUID | None


class CreatedDepositResponse(BaseModel):
    created_deposit_id: uuid.UUID
    created_deposit_transaction_id: uuid.UUID


class CloseDepositRequest(BaseModel):
    deposit_id: uuid.UUID


class ClosedDepositResponse(BaseModel):
    closed_deposit_id: uuid.UUID
    created_deposit_transaction_id: uuid.UUID


class UpdateDepositRequest(BaseModel):
    name: str


class UpdatedDepositResponse(BaseModel):
    updated_deposit_id: uuid.UUID


class DeletedDepositResponse(BaseModel):
    deleted_deposit_id: uuid.UUID
