import uuid

from backend.api.schemas import BaseModel, TunedModel


class ShowTag(TunedModel):
    id: uuid.UUID
    name: str


class TagCreate(BaseModel):
    name: str


class CreatedTagResponse(BaseModel):
    created_tag_id: uuid.UUID


class UpdateTagRequest(BaseModel):
    name: str


class UpdatedTagResponse(BaseModel):
    updated_tag_id: uuid.UUID


class DeletedTadResponse(BaseModel):
    deleted_tag_id: uuid.UUID
