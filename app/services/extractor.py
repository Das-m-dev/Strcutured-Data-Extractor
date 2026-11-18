import httpx
from langsmith import traceable
from pydantic import ValidationError
from app.config import settings
from app.schemas import Invoice
from app.prompts import SYSTEM_PROMPT

SYSTEM_PROMPT = (
    "Extract invoice fields from the text. Use null for anything not present. "
    "Never guess. Return JSON only."
)

class ExtractionError(Exception):
    pass


@traceable(
    run_type="llm",
    name="ollama_chat",
    metadata={"ls_provider": "ollama", "ls_model_name": settings.ollama_model},
)
async def call_ollama(messages: list[dict]) -> dict:
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": Invoice.model_json_schema(),
        "options": {"temperature": 0, "num_ctx": settings.ollama_num_ctx},
        "messages": messages,
        "keep_alive": settings.ollama_keep_alive,
    }
    async with httpx.AsyncClient(timeout=settings.timeout) as client:
        r = await client.post(f"{settings.ollama_host}/api/chat", json=payload)
        r.raise_for_status()
        body = r.json()

    in_tok = body.get("prompt_eval_count", 0)
    out_tok = body.get("eval_count", 0)
    return {
        "message": body["message"],
        "usage_metadata": {
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok,
        },
    }


@traceable(run_type="chain", name="extract_invoice")
async def extract_invoice(text: str) -> Invoice:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    last_err = None
    for _ in range(settings.max_retries + 1):
        result = await call_ollama(messages)
        try:
            return Invoice.model_validate_json(result["message"]["content"])
        except ValidationError as e:
            last_err = e
    raise ExtractionError(f"Model output failed validation: {last_err}")