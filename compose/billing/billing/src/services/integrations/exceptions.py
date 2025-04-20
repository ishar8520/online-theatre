from __future__ import annotations


class UnsupportedIntegrationTypeError(Exception):
    """
    Raised when an unsupported integration type is requested.

    :param integration: the integration type that was not recognized
    """

    pass


class IntegrationCreatePaymentError(Exception):
    """
    Raised when a payment creation via an integration fails.

    :param message: optional error message describing the failure
    """

    pass


class IntegrationRefundPaymentError(Exception):
    """
    Raised when a refund request via an integration fails.

    :param message: optional error message describing the failure
    """

    pass
