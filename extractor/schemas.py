from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


class Invoice(BaseModel):
    """Target schema. OpenAI strict mode: every field required, optional ones are nullable."""

    vendor_name: str = Field(description="Company that issued the invoice")
    invoice_number: Optional[str] = Field(description="Invoice ID, null if absent")
    invoice_date: Optional[str] = Field(description="YYYY-MM-DD, null if absent")
    currency: Optional[str] = Field(description="ISO 4217 code, e.g. USD, JPY, null if unknown")
    total: Optional[float] = Field(description="Final total as stated in the text, null if absent")
    line_items: List[LineItem]


class ExtractionResult(BaseModel):
    """What the pipeline/API returns."""

    invoice: Optional[Invoice]
    attempts: int
    warnings: List[str] = []
    needs_review: bool = False
