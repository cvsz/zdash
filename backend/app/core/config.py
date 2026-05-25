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

    content_pipeline_enabled: bool = Field(default=True, alias='CONTENT_PIPELINE_ENABLED')
    content_store: str = Field(default='in_memory', alias='CONTENT_STORE')
    editor_agent_enabled: bool = Field(default=True, alias='EDITOR_AGENT_ENABLED')
    graphic_agent_enabled: bool = Field(default=True, alias='GRAPHIC_AGENT_ENABLED')
    social_agent_enabled: bool = Field(default=True, alias='SOCIAL_AGENT_ENABLED')
    content_default_brand: str = Field(default='zDash', alias='CONTENT_DEFAULT_BRAND')
    content_default_language: str = Field(default='en', alias='CONTENT_DEFAULT_LANGUAGE')
    content_default_tone: str = Field(default='professional', alias='CONTENT_DEFAULT_TONE')
    content_require_policy_check: bool = Field(default=True, alias='CONTENT_REQUIRE_POLICY_CHECK')
    image_generation_provider: str = Field(default='mock', alias='IMAGE_GENERATION_PROVIDER')
    image_dry_run: bool = Field(default=True, alias='IMAGE_DRY_RUN')
    image_output_dir: str = Field(default='backend/data/content/images', alias='IMAGE_OUTPUT_DIR')
    social_provider: str = Field(default='mock', alias='SOCIAL_PROVIDER')
    social_dry_run: bool = Field(default=True, alias='SOCIAL_DRY_RUN')
    social_approval_required: bool = Field(default=True, alias='SOCIAL_APPROVAL_REQUIRED')
    social_auto_post_enabled: bool = Field(default=False, alias='SOCIAL_AUTO_POST_ENABLED')
    social_default_platforms: str = Field(default='x,tiktok,facebook,instagram,linkedin', alias='SOCIAL_DEFAULT_PLATFORMS')
    social_x_api_key: str = Field(default='', alias='SOCIAL_X_API_KEY')

    iot_enabled: bool = Field(default=True, alias='IOT_ENABLED')
    iot_dry_run: bool = Field(default=True, alias='IOT_DRY_RUN')
    iot_require_confirmation: bool = Field(default=True, alias='IOT_REQUIRE_CONFIRMATION')
    tapo_username: str = Field(default='', alias='TAPO_USERNAME')
    tapo_password: str = Field(default='', alias='TAPO_PASSWORD')
    tapo_device_ip: str = Field(default='', alias='TAPO_DEVICE_IP')
    tapo_device_alias: str = Field(default='zdash-power-node', alias='TAPO_DEVICE_ALIAS')
    backtesting_enabled: bool = Field(default=True, alias='BACKTESTING_ENABLED')
    backtest_dataset_source: str = Field(default='mock', alias='BACKTEST_DATASET_SOURCE')
    backtest_default_symbol: str = Field(default='XAUUSD', alias='BACKTEST_DEFAULT_SYMBOL')
    backtest_default_timeframe: str = Field(default='M5', alias='BACKTEST_DEFAULT_TIMEFRAME')
    backtest_initial_balance: float = Field(default=10000, alias='BACKTEST_INITIAL_BALANCE')
    backtest_default_risk_per_trade_percent: float = Field(default=1, alias='BACKTEST_DEFAULT_RISK_PER_TRADE_PERCENT')
    backtest_commission_per_trade: float = Field(default=0, alias='BACKTEST_COMMISSION_PER_TRADE')
    backtest_spread_points: float = Field(default=25, alias='BACKTEST_SPREAD_POINTS')
    backtest_slippage_points: float = Field(default=5, alias='BACKTEST_SLIPPAGE_POINTS')
    primary_strategy: str = Field(default='ob_aggressive', alias='PRIMARY_STRATEGY')
    allow_strategy_promotion: bool = Field(default=False, alias='ALLOW_STRATEGY_PROMOTION')
    min_promotion_trades: int = Field(default=50, alias='MIN_PROMOTION_TRADES')
    min_promotion_win_rate: float = Field(default=45, alias='MIN_PROMOTION_WIN_RATE')
    min_promotion_profit_factor: float = Field(default=1.2, alias='MIN_PROMOTION_PROFIT_FACTOR')
    max_promotion_drawdown_percent: float = Field(default=20, alias='MAX_PROMOTION_DRAWDOWN_PERCENT')
    max_promotion_consecutive_losses: int = Field(default=8, alias='MAX_PROMOTION_CONSECUTIVE_LOSSES')
    optimizer_max_combinations: int = Field(default=100, alias='OPTIMIZER_MAX_COMBINATIONS')
    optimizer_sort_metric: str = Field(default='profit_factor', alias='OPTIMIZER_SORT_METRIC')

    
    multi_tenant_enabled: bool = Field(default=True, alias='MULTI_TENANT_ENABLED')
    default_org_name: str = Field(default='zDash Local', alias='DEFAULT_ORG_NAME')
    default_workspace_name: str = Field(default='Main Workspace', alias='DEFAULT_WORKSPACE_NAME')
    tenant_header_name: str = Field(default='X-ZDash-Tenant', alias='TENANT_HEADER_NAME')
    workspace_header_name: str = Field(default='X-ZDash-Workspace', alias='WORKSPACE_HEADER_NAME')
    worker_enabled: bool = Field(default=True, alias='WORKER_ENABLED')
    worker_max_retries: int = Field(default=3, alias='WORKER_MAX_RETRIES')
    realtime_enabled: bool = Field(default=True, alias='REALTIME_ENABLED')
    notifications_enabled: bool = Field(default=True, alias='NOTIFICATIONS_ENABLED')
    notification_dry_run: bool = Field(default=True, alias='NOTIFICATION_DRY_RUN')
    cloudflare_dry_run: bool = Field(default=True, alias='CLOUDFLARE_DRY_RUN')

    frontend_origin: str = Field(default='http://localhost:5173', alias='FRONTEND_ORIGIN')
    cors_allow_origins: str = Field(default='http://localhost:5173,http://127.0.0.1:5173', alias='CORS_ALLOW_ORIGINS')

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
