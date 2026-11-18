from fastapi import FastAPI
from app.routers import extract

app = FastAPI(title="Structured Extractor Service", version="1.0.0")
app.include_router(extract.router)

@app.get("/health")
def health():
    return {"status": "ok"}