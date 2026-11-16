from extractor.config import MAX_RETRIES
from extractor.llm import call_llm
from extractor.preprocess import clean_text
from extractor.prompts import SYSTEM_PROMPT, retry_prompt
from extractor.schemas import ExtractionResult
from extractor.validators import check_business_rules


def extract_invoice(text: str) -> ExtractionResult:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": clean_text(text)},
    ]

    invoice, errors = None, []
    for attempt in range(1, MAX_RETRIES + 1):
        invoice = call_llm(messages)
        if invoice is None:
            return ExtractionResult(
                invoice=None, attempts=attempt,
                warnings=["Model refused or returned nothing."], needs_review=True,
            )

        errors = check_business_rules(invoice)
        if not errors:
            return ExtractionResult(invoice=invoice, attempts=attempt)

        messages.append({"role": "assistant", "content": invoice.model_dump_json()})
        messages.append({"role": "user", "content": retry_prompt(errors)})

    return ExtractionResult(
        invoice=invoice, attempts=MAX_RETRIES, warnings=errors, needs_review=True
    )
