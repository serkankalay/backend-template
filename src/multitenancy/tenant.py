from __future__ import annotations

from typing import Callable, TypeVar

from sqlalchemy.orm import Session

from src.data_model import Tenant

NoReturnFunction = TypeVar("NoReturnFunction", bound=Callable[..., None])


def get(session: Session) -> list[Tenant]:
    return list(
        session.query(Tenant)
        .filter(Tenant.filter_deleted_out())
        .filter(Tenant.active.is_(True))
        .all()
    )
