from fastapi import FastAPI
from pydantic import BaseModel

from extractor.pipeline import extract_invoice
from extractor.schemas import ExtractionResult

app = FastAPI(title="Structured Data Extractor")


class ExtractRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractionResult)
def extract(req: ExtractRequest):
    return extract_invoice(req.text)
