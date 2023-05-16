

from pydantic import BaseModel, Field


class TunedModel(BaseModel):
    class Config:
        orm_mode = True