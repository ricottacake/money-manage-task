import uuid

from fastapi import HTTPException


class AccountNotFound(HTTPException):
    def __init__(self, account_id: uuid.UUID, *args, **kwargs):
        super(AccountNotFound, self).__init__(
            status_code=404,
            detail=f"Account with id '{account_id}' not found!",
            *args,
            **kwargs
        )


class TransactionTypeNotFound(HTTPException):
    def __init__(self, transaction_type_id: int, *args, **kwargs):
        super(TransactionTypeNotFound, self).__init__(
            status_code=404,
            detail=f"TransactionType with id '{transaction_type_id}' not found!",
            *args,
            **kwargs
        )


class TransactionNotFound(HTTPException):
    def __init__(self, transaction_id: uuid.UUID, *args, **kwargs):
        super(TransactionNotFound, self).__init__(
            status_code=404,
            detail=f"Transaction with id '{transaction_id}' not found!",
            *args,
            **kwargs
        )


class TagNotFound(HTTPException):
    def __init__(self, tag_id: uuid.UUID, *args, **kwargs):
        super(TagNotFound, self).__init__(
            status_code=404,
            detail=f"Tag with id '{tag_id}' not found!",
            *args,
            **kwargs
        )


class CurrencyNotFound(HTTPException):
    def __init__(self, currency_id: int, *args, **kwargs):
        super(CurrencyNotFound, self).__init__(
            status_code=404,
            detail=f"Currency with id '{currency_id}' not found!",
            *args,
            **kwargs
        )


class TransferTransactionChange(HTTPException):
    def __init__(self, *args, **kwargs):
        super(TransferTransactionChange, self).__init__(
            status_code=422,
            detail=f"Сan not update or delete a transfer transaction! "
                   f"Also can not update transaction to transfer transaction!",
            *args,
            **kwargs
        )
