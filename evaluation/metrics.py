FIELDS = ["vendor_name", "invoice_number", "invoice_date", "currency", "total", "line_items"]


def _norm(v):
    return v.strip().lower() if isinstance(v, str) else v


def field_correct(field: str, pred: dict | None, truth: dict) -> bool:
    if pred is None:
        return False
    p, t = pred.get(field), truth.get(field)
    if field == "total":
        if p is None or t is None:
            return p == t
        return abs(p - t) < 0.01
    if field == "line_items":
        key = lambda items: sorted((round(i["quantity"], 2), round(i["unit_price"], 2)) for i in items)
        return key(p or []) == key(t or [])
    return _norm(p) == _norm(t)


def score(preds: list[dict | None], truths: list[dict]) -> dict[str, float]:
    n = len(truths)
    return {
        f: sum(field_correct(f, p, t) for p, t in zip(preds, truths)) / n
        for f in FIELDS
    }
