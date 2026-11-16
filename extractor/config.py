import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_INPUT_CHARS = 20_000  # guard for very long documents
