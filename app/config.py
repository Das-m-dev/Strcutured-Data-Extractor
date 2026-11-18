from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv() 

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "ollama"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma2:9b"
    ollama_num_ctx: int = 8192

    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    timeout: float = 120.0
    max_retries: int = 2

settings = Settings()