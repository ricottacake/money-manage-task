import uuid
from typing import Sequence
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import requests

from backend.api.schemas.transfer import TransferCreate, ShowTransfer, CreatedTransferResponse
from backend.db.dals import TransactionDAL, TransactionTypeDAL, AccountDAL, CurrencyDAL
from backend.db.session import get_db, TRANSACTION_TYPE_DATA
from backend.exception import AccountNotFound
from config import EXCHANGE_RATE_API_URL, EXCHANGE_RATE_API_KEY


router = APIRouter(
    prefix="/transfer"
)


async def _create_new_transfer(request_body: TransferCreate, db) -> CreatedTransferResponse | None:
    async with db as session:
        async with session.begin():
            account_dal = AccountDAL(session)
            account_from = await account_dal.get_account_by_id(request_body.from_account_id)
            account_to = await account_dal.get_account_by_id(request_body.to_account_id)

            if account_from.balance < request_body.amount_from:
                raise HTTPException(
                    status_code=422,
                    detail="The account balance must not be less than the transfer amount!"
                )

            currency_dal = CurrencyDAL(session)
            currency_from = await currency_dal.get_currency_by_id(account_from.currency_id)
            currency_to = await currency_dal.get_currency_by_id(account_to.currency_id)

            response = requests.get(
                EXCHANGE_RATE_API_URL +
                f"?from={currency_from.name}&to={currency_to.name}&amount={request_body.amount_from}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500)

            amount_to = response.json().get("result")

            transaction_dal = TransactionDAL(session)

            checkpoint = session.begin_nested()
            try:
                transaction_from = await transaction_dal.create_transaction(
                    transaction_type_id=TRANSACTION_TYPE_DATA[2]["id"],
                    amount=request_body.amount_from,
                    account_id=request_body.from_account_id
                )

                transaction_to = await transaction_dal.create_transaction(
                    transaction_type_id=TRANSACTION_TYPE_DATA[3]["id"],
                    amount=amount_to,
                    account_id=request_body.to_account_id,
                    created_at=transaction_from.created_at
                )
            except Exception as exception:
                checkpoint.rollback()
                raise exception

            return CreatedTransferResponse(
                created_from_transaction_id=transaction_from.id,
                created_to_transaction_id=transaction_to.id
            )


@router.post("/")
async def create_transfer(
        request_body: TransferCreate, db: AsyncSession = Depends(get_db)
) -> CreatedTransferResponse:
    try:
        created_transfer_response = await _create_new_transfer(request_body, db)
    except (AccountNotFound, HTTPException) as exception:
        raise exception

    return created_transfer_response
