from typing import Optional

from openai import OpenAI

from extractor.config import MODEL
from extractor.schemas import Invoice

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def call_llm(messages: list[dict]) -> Optional[Invoice]:
    """The ONLY function that talks to the LLM provider. Swap providers here."""
    response = _get_client().responses.parse(
        model=MODEL,
        input=messages,
        text_format=Invoice,
    )
    return response.output_parsed  
