import uuid

from pydantic import Field

from backend.api.schemas import BaseModel


class TransferCreate(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_from: float = Field(1000, gt=0, lt=10**10)


class CreatedTransferResponse(BaseModel):
    created_from_transaction_id: uuid.UUID
    created_to_transaction_id: uuid.UUID
