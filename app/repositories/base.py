"""Generic repository base implementing common CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository providing shared query helpers.

    Subclasses set ``model`` and inherit create/get/list/delete behaviour.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, id_: int) -> ModelT | None:
        return self.db.get(self.model, id_)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()

    def count(self) -> int:
        from sqlalchemy import func

        return self.db.scalar(select(func.count()).select_from(self.model)) or 0

    def filter(self, **filters: Any) -> list[ModelT]:
        stmt = select(self.model)
        for key, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
        return list(self.db.scalars(stmt).all())
