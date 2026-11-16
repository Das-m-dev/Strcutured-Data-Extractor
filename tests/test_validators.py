from extractor.schemas import Invoice, LineItem
from extractor.validators import check_business_rules
from evaluation.metrics import score


def make(**kw):
    base = dict(vendor_name="X", invoice_number=None, invoice_date=None,
                currency=None, total=None, line_items=[])
    base.update(kw)
    return Invoice(**base)


def test_valid_invoice_has_no_errors():
    inv = make(total=85.0, currency="USD", invoice_date="2026-03-03",
               line_items=[LineItem(description="a", quantity=200, unit_price=0.25),
                           LineItem(description="b", quantity=1, unit_price=35.0)])
    assert check_business_rules(inv) == []


def test_total_mismatch_detected():
    inv = make(total=999.0, line_items=[LineItem(description="a", quantity=1, unit_price=10)])
    assert any("sum" in e for e in check_business_rules(inv))


def test_bad_date_and_currency_detected():
    errs = check_business_rules(make(invoice_date="03/03/2026", currency="usd"))
    assert len(errs) == 2


def test_metrics_perfect_score():
    truth = {"vendor_name": "A", "invoice_number": None, "invoice_date": None,
             "currency": "USD", "total": 5.0, "line_items": []}
    assert all(v == 1.0 for v in score([truth], [truth]).values())
