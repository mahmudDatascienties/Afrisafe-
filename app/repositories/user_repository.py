"""Repository for :class:`User` persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for users."""

    model = User

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, id_: int) -> User | None:  # type: ignore[override]
        return self.db.get(User, id_)

    def email_exists(self, email: str) -> bool:
        return self.db.scalar(select(User.id).where(User.email == email)) is not None
