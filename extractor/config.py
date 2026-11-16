import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama or openai

# OpenAI
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

# Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192")) 

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_INPUT_CHARS = 20_000