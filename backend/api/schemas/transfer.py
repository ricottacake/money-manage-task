import uuid

from backend.api.schemas import BaseModel


class TransferCreate(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_from: float


class CreatedTransferResponse(BaseModel):
    created_from_transaction_id: uuid.UUID
    created_to_transaction_id: uuid.UUID
