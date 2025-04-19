from __future__ import annotations


class UnsupportedIntegrationType(Exception):
    pass


class IntegrationCreatePaymentError(Exception):
    pass


class IntegrationRefundPaymentError(Exception):
    pass
