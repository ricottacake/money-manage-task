from backend.api.schemas import BaseModel, TunedModel


class ShowCurrency(TunedModel):
    id: int
    name: str


class CurrencyCreate(BaseModel):
    name: str
