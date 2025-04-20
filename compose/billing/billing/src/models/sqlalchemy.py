from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    UUID,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Text,
    UniqueConstraint,
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
    """
    Базовый класс для всех моделей схемы 'billing'.

    Определяет общую метадату с конвенциями именования для всех таблиц.
    """

    metadata = billing_metadata_obj


class PurchaseItem(BillingBase):
    """
    Модель позиции покупки из таблицы 'purchase_item'.

    :param id: UUID записи позиции
    :param payment_id: ссылка на платёж (payment.id)
    :param name: наименование товара или услуги
    :param quantity: количество единиц
    :param type: тип позиции (текстовое описание)
    :param price: цена за единицу
    :param created_at: время создания записи
    :param modified_at: время последнего обновления записи
    :param payment: связь с объектом Payment
    :param properties: список свойств позиции (PurchaseItemProperty)
    """

    __tablename__ = 'purchase_item'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('billing.payment.id', ondelete='CASCADE'),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
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
        "Payment", cascade='all, delete', back_populates="items"
    )

    properties: Mapped[list[PurchaseItemProperty]] = relationship(
        "PurchaseItemProperty", cascade='all, delete', back_populates="purchase_item"
    )


class PurchaseItemProperty(BillingBase):
    """
    Модель свойства позиции покупки из таблицы 'purchase_item_property'.

    :param id: UUID записи свойства
    :param purchase_item_id: ссылка на позицию (purchase_item.id)
    :param name: наименование свойства
    :param code: код свойства (для уникальности)
    :param value: значение свойства
    :param created_at: время создания записи
    :param purchase_item: связь с объектом PurchaseItem
    """

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
        "PurchaseItem", cascade='all, delete', back_populates="properties"
    )


class Payment(BillingBase):
    """
    Модель платежа из таблицы 'payment'.

    :param id: UUID платежа
    :param user_id: UUID пользователя, создавшего платёж
    :param price: итоговая сумма платежа
    :param ps_name: название платёжной системы (опционально)
    :param ps_invoice_id: UUID счёта в платёжной системе (опционально)
    :param status: статус платежа (строка)
    :param created_at: время создания платежа
    :param modified_at: время последнего обновления платежа
    :param items: список позиций покупки (PurchaseItem)
    """

    __tablename__ = 'payment'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
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

    items: Mapped[list[PurchaseItem]] = relationship(
        "PurchaseItem",
        cascade="all, delete",
        back_populates="payment"
    )
