from functools import lru_cache

from pydantic import Field, field_validator
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
    live_trading_ack: bool = Field(default=False, alias='LIVE_TRADING_ACK')

    risk_guardian_enabled: bool = Field(default=True, alias='RISK_GUARDIAN_ENABLED')
    max_daily_drawdown_percent: float = Field(default=5.0, alias='MAX_DAILY_DRAWDOWN_PERCENT')
    max_total_drawdown_percent: float = Field(default=20.0, alias='MAX_TOTAL_DRAWDOWN_PERCENT')
    emergency_kill_switch_drawdown_percent: float = Field(default=50.0, alias='EMERGENCY_KILL_SWITCH_DRAWDOWN_PERCENT')

    soft_halt_drawdown_level_1: float = Field(default=5.0, alias='SOFT_HALT_DRAWDOWN_LEVEL_1')
    soft_halt_drawdown_level_2: float = Field(default=10.0, alias='SOFT_HALT_DRAWDOWN_LEVEL_2')
    soft_halt_drawdown_level_3: float = Field(default=20.0, alias='SOFT_HALT_DRAWDOWN_LEVEL_3')

    allow_manual_resume: bool = Field(default=True, alias='ALLOW_MANUAL_RESUME')
    require_resume_reason: bool = Field(default=True, alias='REQUIRE_RESUME_REASON')
    hard_halt_on_daily_drawdown: bool = Field(default=False, alias='HARD_HALT_ON_DAILY_DRAWDOWN')


    scheduler_enabled: bool = Field(default=True, alias='SCHEDULER_ENABLED')
    scheduler_timezone: str = Field(default='Asia/Bangkok', alias='SCHEDULER_TIMEZONE')
    scheduler_default_max_runtime_seconds: int = Field(default=300, alias='SCHEDULER_DEFAULT_MAX_RUNTIME_SECONDS')
    scheduler_allow_manual_run: bool = Field(default=True, alias='SCHEDULER_ALLOW_MANUAL_RUN')
    scheduler_store: str = Field(default='in_memory', alias='SCHEDULER_STORE')

    friday_agent_enabled: bool = Field(default=True, alias='FRIDAY_AGENT_ENABLED')

    iot_enabled: bool = Field(default=True, alias='IOT_ENABLED')
    iot_dry_run: bool = Field(default=True, alias='IOT_DRY_RUN')
    iot_require_confirmation: bool = Field(default=True, alias='IOT_REQUIRE_CONFIRMATION')
    tapo_username: str = Field(default='', alias='TAPO_USERNAME')
    tapo_password: str = Field(default='', alias='TAPO_PASSWORD')
    tapo_device_ip: str = Field(default='', alias='TAPO_DEVICE_IP')
    tapo_device_alias: str = Field(default='zdash-power-node', alias='TAPO_DEVICE_ALIAS')
    @field_validator(
        'max_daily_drawdown_percent',
        'max_total_drawdown_percent',
        'emergency_kill_switch_drawdown_percent',
        'soft_halt_drawdown_level_1',
        'soft_halt_drawdown_level_2',
        'soft_halt_drawdown_level_3',
        mode='before',
    )
    @classmethod
    def _safe_positive_threshold(cls, value):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.0
        if parsed < 0:
            return 0.0
        return parsed


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    # Fail-safe normalization to prevent unsafe threshold combinations.
    if settings.max_daily_drawdown_percent <= 0:
        settings.max_daily_drawdown_percent = 5.0
    if settings.max_total_drawdown_percent <= 0:
        settings.max_total_drawdown_percent = 20.0
    if settings.emergency_kill_switch_drawdown_percent <= 0:
        settings.emergency_kill_switch_drawdown_percent = 50.0

    if settings.soft_halt_drawdown_level_1 <= 0:
        settings.soft_halt_drawdown_level_1 = 5.0
    if settings.soft_halt_drawdown_level_2 <= 0:
        settings.soft_halt_drawdown_level_2 = 10.0
    if settings.soft_halt_drawdown_level_3 <= 0:
        settings.soft_halt_drawdown_level_3 = 20.0

    ordered = sorted(
        [
            settings.soft_halt_drawdown_level_1,
            settings.soft_halt_drawdown_level_2,
            settings.soft_halt_drawdown_level_3,
        ]
    )
    settings.soft_halt_drawdown_level_1, settings.soft_halt_drawdown_level_2, settings.soft_halt_drawdown_level_3 = ordered

    return settings
