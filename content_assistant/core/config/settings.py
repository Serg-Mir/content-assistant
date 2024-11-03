from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    DATABASE_URL: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    uvicorn_host: str
    uvicorn_port: int
    environment: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache(maxsize=1)
def get_settings():
    return Settings()
