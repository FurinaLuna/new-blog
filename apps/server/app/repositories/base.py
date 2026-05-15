from typing import TypeVar, Generic
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    def __init__(self, model_class: type[Model], db: AsyncSession):
        self.model_class = model_class
        self.db = db

    async def get_by_id(self, id: str) -> Model | None:
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(self, field_name: str, value) -> Model | None:
        result = await self.db.execute(
            select(self.model_class).where(getattr(self.model_class, field_name) == value)
        )
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[Model]:
        result = await self.db.execute(
            select(self.model_class).offset(offset).limit(limit)
        )
        return list(result.scalars())

    async def count(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(self.model_class)
        )
        return result.scalar() or 0

    async def create(self, **kwargs) -> Model:
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def update(self, instance, **kwargs) -> Model:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def delete(self, instance) -> None:
        await self.db.delete(instance)
