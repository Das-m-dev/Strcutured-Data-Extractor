SYSTEM_PROMPT = """You extract invoice data from unstructured text into the given schema.

Rules:
- Use only information explicitly present in the text. Never guess.
- If a field is missing, return null (or an empty list for line_items).
- Dates must be YYYY-MM-DD. Convert Japanese dates (e.g. 2026年10月5日 -> 2026-10-05).
- Numbers must be plain numbers without currency symbols or thousands separators.
- currency is an ISO 4217 code (円 -> JPY, $ -> USD).
- total is the final amount stated in the document; do not compute it yourself.
"""


def retry_prompt(errors: list[str]) -> str:
    return (
        "Your previous extraction failed validation:\n- "
        + "\n- ".join(errors)
        + "\nRe-read the original text carefully and return a corrected extraction. "
        "If the text itself is inconsistent, keep the stated values."
    )
