"""Payment provider integration boundary.

Add a concrete provider by implementing the PaymentProvider protocol and
registering it in get_payment_provider(). The service layer never imports
a provider directly — it only uses this interface.
"""

from typing import Protocol


class PaymentResult:
    def __init__(self, success: bool, provider_reference: str | None, message: str) -> None:
        self.success = success
        self.provider_reference = provider_reference
        self.message = message


class PaymentProvider(Protocol):
    def charge(
        self,
        amount: float,
        currency: str,
        reference: str,
        description: str | None = None,
    ) -> PaymentResult: ...


def get_payment_provider() -> PaymentProvider:
    """Return the configured payment provider.

    Currently returns a no-op stub. Configure a real provider (e.g. Flutterwave,
    Stripe, MTN MoMo) by implementing PaymentProvider and swapping it in here.
    """
    return _NoOpProvider()


class _NoOpProvider:
    def charge(
        self,
        amount: float,
        currency: str,
        reference: str,
        description: str | None = None,
    ) -> PaymentResult:
        import structlog
        structlog.get_logger(__name__).warning(
            "payment_provider_not_configured",
            reference=reference,
            amount=amount,
            currency=currency,
        )
        return PaymentResult(
            success=False,
            provider_reference=None,
            message="No payment provider configured.",
        )
