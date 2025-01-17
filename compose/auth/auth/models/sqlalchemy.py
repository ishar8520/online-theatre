from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    UUID,
    TEXT,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from ..db.sqlalchemy import AuthBase


class User(AuthBase):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    login: Mapped[str] = mapped_column(TEXT, unique=True)
    password: Mapped[str] = mapped_column(TEXT)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )


class Role(AuthBase):
    __tablename__ = 'role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(TEXT)
    code: Mapped[str] = mapped_column(TEXT, unique=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )


class UserRole(AuthBase):
    __tablename__ = 'user_role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.user.id'))
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.role.id'))
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uix_auth_role_id_user_id'),
    )
