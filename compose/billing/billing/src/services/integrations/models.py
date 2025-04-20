from __future__ import annotations

import enum


class PaymentIntegrations(enum.StrEnum):
    """
    Enum of supported payment integration providers.

    Attributes:
        YOOMONEY: Integration with YooMoney payment provider.

    """

    YOOMONEY = "yoomoney"
