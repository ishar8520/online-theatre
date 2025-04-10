import uuid
from datetime import datetime
from typing import Literal, List

from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Integer, String,
                        Text, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()

AutoPaymentPeriodLiteral = Literal["monthly", "yearly"]
TransactionStatusLiteral = Literal["pending", "completed", "failed"]


class Tariff(Base):
    __tablename__ = "tariffs"
    __table_args__ = (
        CheckConstraint(
            "auto_payment_period IN ('monthly', 'yearly')",
            name="check_auto_payment_period"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_payment_period: Mapped[AutoPaymentPeriodLiteral] = mapped_column(String(50), nullable=False)

    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="tariff",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"Tariff ({self.id}) {self.name}"

    def get_period_in_days(self) -> int:
        period2days = {
            "monthly": 30,
            "yearly": 365,
        }
        return period2days[self.auto_payment_period]


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    tariff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    payment_method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    next_payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=True
    )

    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="subscriptions")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="subscription",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"Subscription ({self.id})"


class MoviePurchase(Base):
    __tablename__ = "movie_purchases"
    __table_args__ = (
        CheckConstraint(
            "payment_status IN ('pending', 'completed', 'failed')",
            name="check_movie_purchase_payment_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    movie_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    payment_status: Mapped[TransactionStatusLiteral] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __str__(self):
        return f"MoviePurchase ({self.id}) {self.payment_status}"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        # Ограничение гарантирует, что заполнено ровно одно из полей: либо subscription_id, либо movie_purchase_id.
        CheckConstraint(
            "((subscription_id IS NOT NULL)::int + (movie_purchase_id IS NOT NULL)::int) = 1",
            name="ck_transaction_one_fk_not_null"
        ),
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed')",
            name="check_transaction_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscriptions.id"),
        nullable=True
    )
    movie_purchase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("movie_purchases.id"),
        nullable=True
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    status: Mapped[TransactionStatusLiteral] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)

    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="transactions",
        foreign_keys=[subscription_id]
    )
    movie_purchase: Mapped["MoviePurchase"] = relationship(
        "MoviePurchase",
        backref="transactions",
        foreign_keys=[movie_purchase_id]
    )

    def __str__(self):
        if self.subscription is not None:
            return f"Transaction for Subscription ({self.subscription.id}) status {self.status}"
        elif self.movie_purchase is not None:
            return f"Transaction for MoviePurchase ({self.movie_purchase.id}) status {self.status}"
        else:
            return f"Transaction ({self.id}) status {self.status}"
