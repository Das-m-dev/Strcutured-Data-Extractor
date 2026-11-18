import httpx
from pydantic import ValidationError
from app.config import settings
from app.schemas import Invoice

SYSTEM_PROMPT = (
    "Extract invoice fields from the text. Use null for anything not present. "
    "Never guess. Return JSON only."
)

class ExtractionError(Exception):
    pass

async def extract_invoice(text: str) -> Invoice:
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": Invoice.model_json_schema(),  # structured output
        "options": {"temperature": 0, "num_ctx": settings.ollama_num_ctx},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }
    last_err = None
    async with httpx.AsyncClient(timeout=settings.timeout) as client:
        for _ in range(settings.max_retries + 1):
            r = await client.post(f"{settings.ollama_host}/api/chat", json=payload)
            r.raise_for_status()
            try:
                return Invoice.model_validate_json(r.json()["message"]["content"])
            except ValidationError as e:
                last_err = e
    raise ExtractionError(f"Model output failed validation: {last_err}")