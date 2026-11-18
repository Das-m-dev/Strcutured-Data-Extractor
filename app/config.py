from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv() # exposes the langsmith to the langsmith SDK

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "ollama"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma2:9b"
    ollama_num_ctx: int = 8192
    ollama_keep_alive: str = "30m"   # keep model in memory between requests
    cache_ttl_seconds: int = 3600
    cache_max_items: int = 500

    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    timeout: float = 120.0
    max_retries: int = 2

    @property
    def active_model(self) -> str:
        return self.openai_model if self.llm_provider == "openai" else self.ollama_model

settings = Settings()