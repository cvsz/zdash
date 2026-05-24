from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='zDash', alias='APP_NAME')
    app_env: str = Field(default='development', alias='APP_ENV')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')

    backend_host: str = Field(default='0.0.0.0', alias='BACKEND_HOST')
    backend_port: int = Field(default=8000, alias='BACKEND_PORT')

    claude_api_key: str = Field(default='', alias='CLAUDE_API_KEY')
    claude_model: str = Field(default='claude-sonnet-4-5', alias='CLAUDE_MODEL')
    ai_provider: str = Field(default='mock', alias='AI_PROVIDER')

    dry_run: bool = Field(default=True, alias='DRY_RUN')


@lru_cache
def get_settings() -> Settings:
    return Settings()
