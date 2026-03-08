from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "MIVE"
    debug: bool = False
    # Database
    database_url: str = "postgresql+asyncpg://mive:mive@localhost:5432/mive"
    database_url_sync: str = "postgresql://mive:mive@localhost:5432/mive"
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    # LLM / Embeddings
    openai_api_key: str = ""
    openai_base_url: str | None = None
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    # Ingestion
    alpha_vantage_api_key: str = ""
    fed_rss_url: str = "https://www.federalreserve.gov/feeds/press_all.xml"
    ecb_rss_url: str = "https://www.ecb.europa.eu/rss/press.html"
    ingestion_interval_minutes: int = 15
    # Clustering
    clustering_window_hours: int = 48
    min_cluster_size: int = 2
    min_samples: int = 1
    # Auto-trigger
    auto_trigger_surprise_threshold_sd: float = 0.3
    auto_trigger_heat_threshold: int = 70
    simulation_cooldown_seconds: int = 300
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
