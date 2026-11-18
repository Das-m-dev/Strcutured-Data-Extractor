import time
import httpx
from fastapi import APIRouter, HTTPException
from app.config import settings
from app.schemas import ExtractRequest, ExtractResponse
from app.services.extractor import extract_invoice, ExtractionError

router = APIRouter(prefix="/v1", tags=["extract"])

@router.post("/extract", response_model=ExtractResponse)
async def extract(req: ExtractRequest):
    start = time.perf_counter()
    try:
        data = await extract_invoice(req.text)
    except httpx.ConnectError:
        raise HTTPException(503, "LLM backend (Ollama) is not reachable")
    except httpx.TimeoutException:
        raise HTTPException(504, "LLM backend timed out")
    except ExtractionError as e:
        raise HTTPException(502, str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"Ollama error {e.response.status_code}: {e.response.text}")
    return ExtractResponse(
        data=data,
        model=settings.ollama_model,
        latency_ms=int((time.perf_counter() - start) * 1000),
    )