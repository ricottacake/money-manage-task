import uuid

from fastapi import HTTPException


class ProjectBaseException(HTTPException):
    pass


class AccountNotFound(ProjectBaseException):
    def __init__(self, account_id: uuid.UUID, *args, **kwargs):
        super(AccountNotFound, self).__init__(
            status_code=404,
            detail=f"Account with id '{account_id}' not found!",
            *args,
            **kwargs
        )


class TransactionTypeNotFound(ProjectBaseException):
    def __init__(self, transaction_type_id: int, *args, **kwargs):
        super(TransactionTypeNotFound, self).__init__(
            status_code=404,
            detail=f"TransactionType with id '{transaction_type_id}' not found!",
            *args,
            **kwargs
        )


class TransactionNotFound(ProjectBaseException):
    def __init__(self, transaction_id: uuid.UUID, *args, **kwargs):
        super(TransactionNotFound, self).__init__(
            status_code=404,
            detail=f"Transaction with id '{transaction_id}' not found!",
            *args,
            **kwargs
        )


class TagNotFound(ProjectBaseException):
    def __init__(self, tag_id: uuid.UUID, *args, **kwargs):
        super(TagNotFound, self).__init__(
            status_code=404,
            detail=f"Tag with id '{tag_id}' not found!",
            *args,
            **kwargs
        )


class CurrencyNotFound(ProjectBaseException):
    def __init__(self, currency_id: int, *args, **kwargs):
        super(CurrencyNotFound, self).__init__(
            status_code=404,
            detail=f"Currency with id '{currency_id}' not found!",
            *args,
            **kwargs
        )


class CreditNotFound(ProjectBaseException):
    def __init__(self, credit_id: uuid.UUID, *args, **kwargs):
        super(CreditNotFound, self).__init__(
            status_code=404,
            detail=f"Credit with id '{credit_id}' not found!",
            *args,
            **kwargs
        )


class CreditAlreadyClosed(ProjectBaseException):
    def __init__(self, credit_id: uuid.UUID, *args, **kwargs):
        super(CreditAlreadyClosed, self).__init__(
            status_code=422,
            detail=f"Credit with id '{credit_id}' is already closed!",
            *args,
            **kwargs
        )


class ReservedTransactionChange(ProjectBaseException):
    def __init__(self, *args, **kwargs):
        super(ReservedTransactionChange, self).__init__(
            status_code=422,
            detail=f"Сan not update or delete a reserved transaction! "
                   f"Also can not update transaction to reserved transaction!",
            *args,
            **kwargs
        )
