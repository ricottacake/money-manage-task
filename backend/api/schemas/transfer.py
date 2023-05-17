import uuid
from datetime import datetime

from backend.api.schemas import BaseModel, TunedModel


class ShowTransfer(TunedModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_from: float
    amount_to: float
    exchange_rate: float
    created_at: datetime


class TransferCreate(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_from: float


class CreatedTransferResponse(BaseModel):
    created_from_transaction_id: uuid.UUID
    created_to_transaction_id: uuid.UUID
