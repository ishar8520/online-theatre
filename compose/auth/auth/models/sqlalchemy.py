from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    UUID,
    TEXT,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
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
    roles: Mapped[list[UserRole]] = relationship(
        "UserRole", cascade="all, delete-orphan", back_populates="user"
    )
    login_history: Mapped[list[LoginHistory]] = relationship(
        "LoginHistory", cascade="all, delete-orphan", back_populates="user"
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
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole", cascade="all, delete-orphan", back_populates="role"
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
        UniqueConstraint(
            'user_id',
            'role_id',
            name='uix_auth_role_id_user_id'
        ),
    )
    user: Mapped[User] = relationship("User", back_populates="roles")
    role: Mapped[Role] = relationship("Role", back_populates="user_roles")


class LoginHistory(AuthBase):
    __tablename__ = 'login_history'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.user.id'))
    user_agent: Mapped[str] = mapped_column(TEXT)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    __table_args__ = (
        Index('ix_login_history_user_id', 'user_id'),
    )
    user: Mapped[User] = relationship("User", back_populates="login_history")
