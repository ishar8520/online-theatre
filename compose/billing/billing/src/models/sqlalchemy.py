from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    MetaData,
    UUID,
    Text,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Integer,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

billing_metadata_obj = MetaData(
    schema='billing',
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    },
)


class BillingBase(DeclarativeBase):
    metadata = billing_metadata_obj


class PurchaseItem(BillingBase):
    __tablename__ = 'purchase_item'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('billing.payment.id', ondelete='CASCADE'),
        nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    sum: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    payment: Mapped[Payment] = relationship(
        "Payment", cascade='all, delete', back_populates="purchase_item"
    )
    purchase_item_property: Mapped[list[PurchaseItemProperty]] = relationship(
        "PurchaseItemProperty", cascade='all, delete', back_populates="purchase_item"
    )


class PurchaseItemProperty(BillingBase):
    __tablename__ = 'purchase_item_property'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    purchase_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('billing.purchase_item.id', ondelete='CASCADE')
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    __table_args__ = (
        UniqueConstraint('purchase_item_id', 'code'),
    )

    purchase_item: Mapped[PurchaseItem] = relationship(
        "PurchaseItem", cascade='all, delete', back_populates="purchase_item_property"
    )


class Payment(BillingBase):
    __tablename__ = 'payment'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    ps_name: Mapped[str] = mapped_column(Text, nullable=True)
    ps_invoice_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    purchase_item: Mapped[list[PurchaseItem]] = relationship(
        "PurchaseItem", back_populates="payment", cascade='all, delete'
    )
