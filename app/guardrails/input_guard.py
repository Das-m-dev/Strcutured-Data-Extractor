import re
from dataclasses import dataclass, field

MAX_CHARS = 8000

INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts?)",
    r"disregard (the )?(system|previous) (prompt|instructions)",
    r"reveal (your |the )?(system )?prompt",
    r"you are now",
    r"act as (an? )?(?!invoice)",
    r"</?system>",
]

PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"(?<!\d)(?:\+?\d{1,3}[-\s]?)?\(?\d{2,4}\)?[-\s]?\d{3,4}[-\s]?\d{3,4}(?!\d)"),
}

class InputRejected(Exception):
    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(message)

@dataclass
class InputResult:
    text: str
    warnings: list[str] = field(default_factory=list)

def check_input(text: str, mask_pii: bool = False) -> InputResult:
    text = text.strip()
    if len(text) < 10:
        raise InputRejected("too_short", "Text is too short to be an invoice.")
    if len(text) > MAX_CHARS:
        raise InputRejected("too_long", f"Text exceeds {MAX_CHARS} characters.")

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise InputRejected("prompt_injection", "Input looks like a prompt injection attempt.")

    warnings = []
    if mask_pii:
        for name, rx in PII_PATTERNS.items():
            if rx.search(text):
                text = rx.sub(f"[{name.upper()}]", text)
                warnings.append(f"{name} masked")
    return InputResult(text=text, warnings=warnings)