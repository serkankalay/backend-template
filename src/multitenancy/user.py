from __future__ import annotations

from sqlalchemy.orm import Session

from src.data_model import User


def try_get(session: Session, user_name: str) -> User | None:
    return (
        session.query(User)
        .filter(User.filter_deleted_out())
        .filter(User.name == user_name)
        .one_or_none()
    )


def get(session: Session, user_id: int) -> User | None:
    return (
        session.query(User)
        .filter(User.filter_deleted_out())
        .filter(User.id == user_id)
        .one_or_none()
    )
