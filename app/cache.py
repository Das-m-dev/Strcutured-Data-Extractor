import hashlib
import time
from collections import OrderedDict
from app.config import settings
from app.prompts import PROMPT_VERSION
from app.schemas import Invoice

class TTLCache:
    def __init__(self, ttl: int, max_items: int):
        self.ttl, self.max_items = ttl, max_items
        self._store: OrderedDict[str, tuple[float, Invoice]] = OrderedDict()

    def get(self, key: str) -> Invoice | None:
        item = self._store.get(key)
        if not item:
            return None
        expires, value = item
        if expires < time.monotonic():
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Invoice) -> None:
        self._store[key] = (time.monotonic() + self.ttl, value)
        self._store.move_to_end(key)
        while len(self._store) > self.max_items:
            self._store.popitem(last=False)  # drop oldest

def make_key(model: str, text: str) -> str:
    raw = f"{PROMPT_VERSION}|{model}|{text.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()

extraction_cache = TTLCache(settings.cache_ttl_seconds, settings.cache_max_items)