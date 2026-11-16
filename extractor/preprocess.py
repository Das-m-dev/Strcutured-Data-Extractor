import re
from pathlib import Path

from extractor.config import MAX_INPUT_CHARS


def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ")           # full-width space (Japanese docs)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_INPUT_CHARS]


def load_text(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF

        with fitz.open(path) as doc:
            return clean_text("\n".join(page.get_text() for page in doc))
    return clean_text(path.read_text(encoding="utf-8"))
