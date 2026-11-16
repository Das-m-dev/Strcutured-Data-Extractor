from typing import Optional

from pydantic import ValidationError

from extractor.config import (
    OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_NUM_CTX, OPENAI_MODEL, PROVIDER,
)
from extractor.schemas import Invoice

_openai_client = None


def _call_openai(messages: list[dict]) -> Optional[Invoice]:
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI

        _openai_client = OpenAI() 
    response = _openai_client.responses.parse(
        model=OPENAI_MODEL, input=messages, text_format=Invoice
    )
    return response.output_parsed  


def _call_ollama(messages: list[dict]) -> Optional[Invoice]:
    import ollama

    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        format=Invoice.model_json_schema(),  # constrains output to the schema
        options={"temperature": 0, "num_ctx": OLLAMA_NUM_CTX},
    )
    try:
        return Invoice.model_validate_json(response.message.content)
    except ValidationError:
        return None


def call_llm(messages: list[dict]) -> Optional[Invoice]:
    """The ONLY function that talks to an LLM provider."""
    if PROVIDER == "openai":
        return _call_openai(messages)
    if PROVIDER == "ollama":
        return _call_ollama(messages)
    raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")
