import json
from pathlib import Path

from extractor.pipeline import extract_invoice
from extractor.preprocess import load_text
from evaluation.metrics import FIELDS, field_correct, score

ROOT = Path(__file__).resolve().parent.parent
SAMPLES, LABELS = ROOT / "data" / "samples", ROOT / "data" / "labels"


def main():
    preds, truths, failures = [], [], []
    for sample in sorted(SAMPLES.glob("*.txt")):
        truth = json.loads((LABELS / f"{sample.stem}.json").read_text(encoding="utf-8"))
        result = extract_invoice(load_text(sample))
        pred = result.invoice.model_dump() if result.invoice else None
        preds.append(pred)
        truths.append(truth)
        bad = [f for f in FIELDS if not field_correct(f, pred, truth)]
        if bad:
            failures.append({"file": sample.name, "wrong_fields": bad, "pred": pred, "truth": truth})

    scores = score(preds, truths)
    print(f"\nDocuments evaluated: {len(truths)}\n")
    for f, s in scores.items():
        print(f"{f:<16}{s:.0%}")
    print(f"\nFailures: {len(failures)}")
    for fail in failures:
        print(f"  - {fail['file']}: {fail['wrong_fields']}")

    (ROOT / "evaluation" / "results.json").write_text(
        json.dumps({"scores": scores, "failures": failures}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
