from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Sequence

from sqlalchemy import ForeignKey, Identity, MetaData, func, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from src.settings import Settings


class Base(DeclarativeBase):
    metadata = MetaData()


class CommonMixin:
    # Can be overridden in deriving classes to set specific start value.
    __identity_start__: int = 1000

    created_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.timezone("UTC", func.now()),
    )

    @declared_attr
    def id(cls) -> Mapped[int]:
        """Dynamically assign the identity start value based on subclass."""
        return mapped_column(
            Identity(start=getattr(cls, "__identity_start__", 1000)),
            primary_key=True,
            autoincrement=True,
        )


class HasTimespanMixin:
    start: Mapped[datetime]
    end: Mapped[datetime]


class DeletableMixin:
    deleted_at: Mapped[Optional[datetime]]

    @classmethod
    def filter_deleted_out(cls) -> Any:
        return cls.deleted_at.is_(None)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class Tenant(CommonMixin, DeletableMixin, Base):
    __tablename__ = "tenant"
    name: Mapped[str]
    schema: Mapped[str]
    default_tenant: Mapped[bool] = mapped_column(
        server_default=text("false"), default=False
    )
    active: Mapped[bool] = mapped_column(
        server_default=text("false"), default=False
    )

    users_raw: Mapped[List[User]] = relationship(
        back_populates="tenant", lazy="dynamic"
    )

    @property
    def users(self) -> Sequence[User]:
        return list(self.users_raw.filter(User.filter_deleted_out()).all())  # type: ignore  # noqa: E501

    __table_args__ = ({"schema": Settings.database.shared_schema},)


class User(CommonMixin, DeletableMixin, Base):
    __tablename__ = "user"
    tenant_id: Mapped[int] = mapped_column(ForeignKey("shared.tenant.id"))
    name: Mapped[str]
    password: Mapped[str]  # Hashed password
    email: Mapped[str]
    active: Mapped[bool] = mapped_column(
        server_default=text("false"), default=False
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users_raw")

    __table_args__ = ({"schema": Settings.database.shared_schema},)
