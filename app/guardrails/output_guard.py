import re
from datetime import datetime
from app.schemas import Invoice

ALLOWED_CURRENCIES = {"JPY", "USD", "EUR", "INR", "IDR"}

class OutputRejected(Exception):
    pass

def check_output(invoice: Invoice, source_text: str) -> list[str]:
    """Raise OutputRejected on hard failures; return a list of soft warnings."""
    warnings = []

    # Hard rules
    if invoice.currency and invoice.currency.upper() not in ALLOWED_CURRENCIES:
        raise OutputRejected(f"Unsupported currency: {invoice.currency}")

    if invoice.date:
        try:
            datetime.strptime(invoice.date, "%Y-%m-%d")
        except ValueError:
            raise OutputRejected(f"Date not in YYYY-MM-DD format: {invoice.date}")

    if invoice.total is not None and invoice.total < 0:
        raise OutputRejected("Total cannot be negative")

    # Leak check: model must not echo its instructions
    leak_markers = ["return json only", "never guess", "few-shot", "system prompt"]
    blob = invoice.model_dump_json().lower()
    if any(m in blob for m in leak_markers):
        raise OutputRejected("Output contains instruction text")

    # Soft rules (warnings)
    if invoice.items and invoice.total is not None:
        computed = sum((i.quantity or 0) * (i.unit_price or 0) for i in invoice.items)
        if computed and abs(computed - invoice.total) > 0.01:
            warnings.append(f"items sum ({computed}) does not match total ({invoice.total})")

    # Grounding: key values should appear in the source text
    if invoice.invoice_number and invoice.invoice_number.lower() not in source_text.lower():
        warnings.append("invoice_number not found in source text (possible hallucination)")
    if invoice.vendor and invoice.vendor.lower() not in source_text.lower():
        warnings.append("vendor not found in source text (possible hallucination)")

    return warnings