from pydantic import BaseModel, Field

class LineItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None

class Invoice(BaseModel):
    vendor: str | None = None
    invoice_number: str | None = None
    date: str | None = None
    currency: str | None = None
    total: float | None = None
    items: list[LineItem] = []

class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)

class ExtractResponse(BaseModel):
    data: Invoice
    model: str
    latency_ms: int
    cached: bool = False
    usage: dict = {}
    warnings: list[str] = []
    