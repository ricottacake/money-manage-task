import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.tag import ShowTag, CreatedTagResponse, TagCreate
from app.db.dals import TagDAL
from app.db.session import get_db


router = APIRouter(
    prefix="/tag"
)


async def _create_new_tag(request_body: TagCreate, db) -> CreatedTagResponse:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)
            tag = await tag_dal.create_tag(name=request_body.name)
            return CreatedTagResponse(created_tag_id=tag.id)


async def _get_tags(db) -> Sequence[ShowTag] | None:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)

            tags = await tag_dal.get_tags()

            return tuple(ShowTag(
                id=tag.id,
                name=tag.name,
            ) for tag in tags)


async def _get_tag_by_id(tag_id: uuid.UUID, db) -> ShowTag:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)

            tag = await tag_dal.get_tag_by_id(
                tag_id=tag_id
            )

            return ShowTag(
                id=tag.id,
                name=tag.name
            )


@router.get("/all/")
async def get_tags(db: AsyncSession = Depends(get_db)) -> Sequence[ShowTag]:
    return await _get_tags(db=db)


@router.get("/", response_model=ShowTag)
async def get_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ShowTag:
    try:
        tag = await _get_tag_by_id(tag_id, db=db)
    except HTTPException as exception:
        raise exception
    return tag


@router.post("/", response_model=CreatedTagResponse)
async def create_tag(
        request_body: TagCreate, db: AsyncSession = Depends(get_db)
) -> CreatedTagResponse:
    created_tag_response = await _create_new_tag(request_body, db=db)
    return created_tag_response
