from datetime import datetime

from extractor.schemas import Invoice


def check_business_rules(inv: Invoice) -> list[str]:
    """Return a list of human-readable problems. Empty list = valid."""
    errors: list[str] = []

    if inv.total is not None and inv.line_items:
        calc = sum(i.quantity * i.unit_price for i in inv.line_items)
        if abs(calc - inv.total) > max(0.01 * abs(inv.total), 0.01):
            errors.append(f"Line items sum to {calc:g} but total is {inv.total:g}.")

    if inv.invoice_date is not None:
        try:
            datetime.strptime(inv.invoice_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"invoice_date '{inv.invoice_date}' is not YYYY-MM-DD.")

    if inv.currency is not None and not (len(inv.currency) == 3 and inv.currency.isupper()):
        errors.append(f"currency '{inv.currency}' is not a 3-letter ISO 4217 code.")

    if inv.total is not None and inv.total < 0:
        errors.append("total is negative.")

    return errors
