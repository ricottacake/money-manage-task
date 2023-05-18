import uuid
from typing import Sequence
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import requests

from backend.api.schemas.transfer import TransferCreate, ShowTransfer, CreatedTransferResponse
from backend.db.dals import TransactionDAL, TransactionTypeDAL, AccountDAL, CurrencyDAL
from backend.db.session import get_db, TRANSACTION_TYPE_DATA
from config import EXCHANGE_RATE_API_URL, EXCHANGE_RATE_API_KEY


router = APIRouter(
    prefix="/transfer"
)


async def _create_new_transfer(body: TransferCreate, db) -> CreatedTransferResponse | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            account_from = await account_dal.get_account_by_id(body.from_account_id)

            if account_from is None or account_from.balance < body.amount_from:
                return

            currency_dal = CurrencyDAL(session)
            currency_from = await currency_dal.get_currency_by_id(account_from.currency_id)

            if currency_from is None:
                return

            account_to = await account_dal.get_account_by_id(body.to_account_id)

            if account_to is None:
                return

            currency_to = await currency_dal.get_currency_by_id(account_to.currency_id)

            if currency_to is None:
                return

            response = requests.get(
                EXCHANGE_RATE_API_URL +
                f"?from={currency_from.name}&to={currency_to.name}&amount={body.amount_from}"
            )

            if response.status_code != 200:
                return

            amount_to = response.json().get("result")

            transaction_dal = TransactionDAL(session)

            transaction_from = await transaction_dal.create_transaction(
                transaction_type_id=TRANSACTION_TYPE_DATA[2]["id"],
                amount=body.amount_from,
                account_id=body.from_account_id
            )

            transaction_to = await transaction_dal.create_transaction(
                transaction_type_id=TRANSACTION_TYPE_DATA[3]["id"],
                amount=amount_to,
                account_id=body.to_account_id,
                created_at=transaction_from.created_at
            )

            if transaction_to is not None:
                return CreatedTransferResponse(
                    created_from_transaction_id=transaction_from.id,
                    created_to_transaction_id=transaction_to.id
                )


@router.post("/")
async def create_transfer(
        body: TransferCreate, db: AsyncSession = Depends(get_db)
) -> CreatedTransferResponse:
    created_transfer_response = await _create_new_transfer(body, db)

    if created_transfer_response is None:
        raise HTTPException(
            status_code=404,
            # detail=f"Not found Account by id"
        )
    return created_transfer_response
