import enum

from pydantic import BaseModel


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class OrderBy(enum.Enum):
    id = "id"
    chronological = "chronological"
    reverse_chronological = "reverse_chronological"
