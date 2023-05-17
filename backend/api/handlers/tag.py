import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.tag import ShowTag
from backend.db.dals import TagDAL
from backend.db.session import get_db


router = APIRouter(
    prefix="/tag"
)


async def _get_tags(db) -> Sequence[ShowTag] | None:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)

            tags = await tag_dal.get_tags()

            return tuple(ShowTag(
                id=tag.id,
                name=tag.name,
            ) for tag in tags)


async def _get_tag_by_id(tag_id: uuid.UUID, db) -> ShowTag | None:
    async with db as session:
        async with session.begin():
            tag_dal = TagDAL(session)

            tag = await tag_dal.get_tag_by_id(
                tag_id=tag_id
            )

            if tag is not None:
                return ShowTag(
                    id=tag.id,
                    name=tag.name
                )


@router.get("/all/")
async def get_tags(db: AsyncSession = Depends(get_db)) -> Sequence[ShowTag]:
    return await _get_tags(db=db)


@router.get("/", response_model=ShowTag)
async def get_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ShowTag:
    return await _get_tag_by_id(tag_id, db=db)
