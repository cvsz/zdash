from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = Field(default="zDash", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8005, alias="BACKEND_PORT")

    database_url: str = Field(default="sqlite:///./zdash.db", alias="DATABASE_URL")
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    production_safety_lock: bool = Field(default=True, alias="PRODUCTION_SAFETY_LOCK")
    production_allow_live_actions: bool = Field(
        default=False, alias="PRODUCTION_ALLOW_LIVE_ACTIONS"
    )
    auth_enabled: bool = Field(default=False, alias="AUTH_ENABLED")
    auth_allow_bootstrap_in_production: bool = Field(
        default=False, alias="AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION"
    )
    metrics_auth_required: bool = Field(default=False, alias="METRICS_AUTH_REQUIRED")
    metrics_allow_unauthenticated_dev: bool = Field(
        default=False, alias="METRICS_ALLOW_UNAUTHENTICATED_DEV"
    )
    jwt_secret_key: str = Field(
        default="dev-only-change-before-production", alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    bootstrap_admin_username: str = Field(
        default="admin", alias="BOOTSTRAP_ADMIN_USERNAME"
    )
    bootstrap_admin_password: str = Field(
        default="dev-only-change-before-production", alias="BOOTSTRAP_ADMIN_PASSWORD"
    )
    default_admin_password: str = Field(
        default="dev-only-change-before-production", alias="DEFAULT_ADMIN_PASSWORD"
    )

    claude_api_key: str = Field(default="", alias="CLAUDE_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-5", alias="CLAUDE_MODEL")
    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")

    trading_enabled: bool = Field(default=True, alias="TRADING_ENABLED")
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    live_trading_ack: bool = Field(default=False, alias="LIVE_TRADING_ACK")
    mt5_enabled: bool = Field(default=False, alias="MT5_ENABLED")
    mt5_login: str = Field(default="", alias="MT5_LOGIN")
    mt5_password: str = Field(default="", alias="MT5_PASSWORD")
    mt5_server: str = Field(default="", alias="MT5_SERVER")
    mt5_path: str = Field(default="", alias="MT5_PATH")
    trading_symbol: str = Field(default="XAUUSD", alias="TRADING_DEFAULT_SYMBOL")
    trading_timeframe: str = Field(default="M5", alias="TRADING_DEFAULT_TIMEFRAME")
    trading_default_strategy: str = Field(
        default="ob_aggressive", alias="TRADING_DEFAULT_STRATEGY"
    )
    trading_max_signal_age_seconds: int = Field(
        default=300, alias="TRADING_MAX_SIGNAL_AGE_SECONDS"
    )
    funnel_fast_period: int = Field(default=21, alias="FUNNEL_FAST_PERIOD")
    funnel_medium_period: int = Field(default=10, alias="FUNNEL_MEDIUM_PERIOD")
    funnel_slow_period: int = Field(default=3, alias="FUNNEL_SLOW_PERIOD")
    ai_trading_analysis_enabled: bool = Field(
        default=True, alias="AI_TRADING_ANALYSIS_ENABLED"
    )
    ai_trading_provider: str = Field(default="mock", alias="AI_TRADING_PROVIDER")

    risk_guardian_enabled: bool = Field(default=True, alias="RISK_GUARDIAN_ENABLED")
    max_daily_drawdown_percent: float = Field(
        default=5.0, alias="MAX_DAILY_DRAWDOWN_PERCENT"
    )
    max_total_drawdown_percent: float = Field(
        default=20.0, alias="MAX_TOTAL_DRAWDOWN_PERCENT"
    )
    emergency_kill_switch_drawdown_percent: float = Field(
        default=50.0, alias="EMERGENCY_KILL_SWITCH_DRAWDOWN_PERCENT"
    )

    soft_halt_drawdown_level_1: float = Field(
        default=5.0, alias="SOFT_HALT_DRAWDOWN_LEVEL_1"
    )
    soft_halt_drawdown_level_2: float = Field(
        default=10.0, alias="SOFT_HALT_DRAWDOWN_LEVEL_2"
    )
    soft_halt_drawdown_level_3: float = Field(
        default=20.0, alias="SOFT_HALT_DRAWDOWN_LEVEL_3"
    )

    allow_manual_resume: bool = Field(default=True, alias="ALLOW_MANUAL_RESUME")
    require_resume_reason: bool = Field(default=True, alias="REQUIRE_RESUME_REASON")
    hard_halt_on_daily_drawdown: bool = Field(
        default=False, alias="HARD_HALT_ON_DAILY_DRAWDOWN"
    )

    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    scheduler_timezone: str = Field(default="Asia/Bangkok", alias="SCHEDULER_TIMEZONE")
    scheduler_default_max_runtime_seconds: int = Field(
        default=300, alias="SCHEDULER_DEFAULT_MAX_RUNTIME_SECONDS"
    )
    scheduler_allow_manual_run: bool = Field(
        default=True, alias="SCHEDULER_ALLOW_MANUAL_RUN"
    )
    scheduler_store: str = Field(default="in_memory", alias="SCHEDULER_STORE")

    friday_agent_enabled: bool = Field(default=True, alias="FRIDAY_AGENT_ENABLED")

    content_pipeline_enabled: bool = Field(
        default=True, alias="CONTENT_PIPELINE_ENABLED"
    )
    content_store: str = Field(default="in_memory", alias="CONTENT_STORE")
    editor_agent_enabled: bool = Field(default=True, alias="EDITOR_AGENT_ENABLED")
    graphic_agent_enabled: bool = Field(default=True, alias="GRAPHIC_AGENT_ENABLED")
    social_agent_enabled: bool = Field(default=True, alias="SOCIAL_AGENT_ENABLED")
    content_default_brand: str = Field(default="zDash", alias="CONTENT_DEFAULT_BRAND")
    content_default_language: str = Field(
        default="en", alias="CONTENT_DEFAULT_LANGUAGE"
    )
    content_default_tone: str = Field(
        default="professional", alias="CONTENT_DEFAULT_TONE"
    )
    content_require_policy_check: bool = Field(
        default=True, alias="CONTENT_REQUIRE_POLICY_CHECK"
    )
    image_generation_provider: str = Field(
        default="mock", alias="IMAGE_GENERATION_PROVIDER"
    )
    image_dry_run: bool = Field(default=True, alias="IMAGE_DRY_RUN")
    image_output_dir: str = Field(
        default="backend/data/content/images", alias="IMAGE_OUTPUT_DIR"
    )
    social_provider: str = Field(default="mock", alias="SOCIAL_PROVIDER")
    social_dry_run: bool = Field(default=True, alias="SOCIAL_DRY_RUN")
    social_approval_required: bool = Field(
        default=True, alias="SOCIAL_APPROVAL_REQUIRED"
    )
    social_auto_post_enabled: bool = Field(
        default=False, alias="SOCIAL_AUTO_POST_ENABLED"
    )
    social_real_posting_approved: bool = Field(
        default=False, alias="SOCIAL_REAL_POSTING_APPROVED"
    )
    social_default_platforms: str = Field(
        default="x,tiktok,facebook,instagram,linkedin", alias="SOCIAL_DEFAULT_PLATFORMS"
    )
    social_x_api_key: str = Field(default="", alias="SOCIAL_X_API_KEY")
    social_x_api_secret: str = Field(default="", alias="SOCIAL_X_API_SECRET")
    social_tiktok_access_token: str = Field(
        default="", alias="SOCIAL_TIKTOK_ACCESS_TOKEN"
    )
    social_facebook_access_token: str = Field(
        default="", alias="SOCIAL_FACEBOOK_ACCESS_TOKEN"
    )
    social_instagram_access_token: str = Field(
        default="", alias="SOCIAL_INSTAGRAM_ACCESS_TOKEN"
    )
    social_linkedin_access_token: str = Field(
        default="", alias="SOCIAL_LINKEDIN_ACCESS_TOKEN"
    )

    iot_enabled: bool = Field(default=True, alias="IOT_ENABLED")
    iot_dry_run: bool = Field(default=True, alias="IOT_DRY_RUN")
    iot_require_confirmation: bool = Field(
        default=True, alias="IOT_REQUIRE_CONFIRMATION"
    )
    iot_real_actions_approved: bool = Field(
        default=False, alias="IOT_REAL_ACTIONS_APPROVED"
    )
    tapo_username: str = Field(default="", alias="TAPO_USERNAME")
    tapo_password: str = Field(default="", alias="TAPO_PASSWORD")
    tapo_device_ip: str = Field(default="", alias="TAPO_DEVICE_IP")
    tapo_device_alias: str = Field(
        default="zdash-power-node", alias="TAPO_DEVICE_ALIAS"
    )

    nssm_service_name: str = Field(
        default="zdash-janie-server", alias="NSSM_SERVICE_NAME"
    )
    nssm_display_name: str = Field(
        default="zDash Janie Server", alias="NSSM_DISPLAY_NAME"
    )
    nssm_description: str = Field(
        default="zDash Janie Server and Agent Runtime", alias="NSSM_DESCRIPTION"
    )
    nssm_backend_host: str = Field(default="127.0.0.1", alias="NSSM_BACKEND_HOST")
    nssm_backend_port: int = Field(default=8005, alias="NSSM_BACKEND_PORT")

    multi_tenant_enabled: bool = Field(default=True, alias="MULTI_TENANT_ENABLED")
    default_org_name: str = Field(default="zDash Local", alias="DEFAULT_ORG_NAME")
    default_workspace_name: str = Field(
        default="Main Workspace", alias="DEFAULT_WORKSPACE_NAME"
    )
    tenant_header_name: str = Field(
        default="X-ZDash-Tenant", alias="TENANT_HEADER_NAME"
    )
    workspace_header_name: str = Field(
        default="X-ZDash-Workspace", alias="WORKSPACE_HEADER_NAME"
    )
    worker_queue_backend: str = Field(
        default="memory", alias="WORKER_QUEUE_BACKEND"
    )
    worker_max_retries: int = Field(default=3, alias="WORKER_MAX_RETRIES")

    cloudflare_dry_run: bool = Field(default=True, alias="CLOUDFLARE_DRY_RUN")
    notification_dry_run: bool = Field(default=True, alias="NOTIFICATION_DRY_RUN")

    backtesting_enabled: bool = Field(default=True, alias="BACKTESTING_ENABLED")
    backtest_dataset_source: str = Field(
        default="mock", alias="BACKTEST_DATASET_SOURCE"
    )
    backtest_default_symbol: str = Field(
        default="XAUUSD", alias="BACKTEST_DEFAULT_SYMBOL"
    )
    backtest_default_timeframe: str = Field(
        default="M5", alias="BACKTEST_DEFAULT_TIMEFRAME"
    )
    backtest_initial_balance: float = Field(
        default=10000, alias="BACKTEST_INITIAL_BALANCE"
    )
    backtest_default_risk_per_trade_percent: float = Field(
        default=1, alias="BACKTEST_DEFAULT_RISK_PER_TRADE_PERCENT"
    )
    backtest_commission_per_trade: float = Field(
        default=0, alias="BACKTEST_COMMISSION_PER_TRADE"
    )
    backtest_spread_points: float = Field(default=25, alias="BACKTEST_SPREAD_POINTS")
    backtest_slippage_points: float = Field(default=5, alias="BACKTEST_SLIPPAGE_POINTS")
    primary_strategy: str = Field(default="ob_aggressive", alias="PRIMARY_STRATEGY")
    allow_strategy_promotion: bool = Field(
        default=False, alias="ALLOW_STRATEGY_PROMOTION"
    )
    min_promotion_trades: int = Field(default=50, alias="MIN_PROMOTION_TRADES")
    min_promotion_win_rate: float = Field(default=45, alias="MIN_PROMOTION_WIN_RATE")
    min_promotion_profit_factor: float = Field(
        default=1.2, alias="MIN_PROMOTION_PROFIT_FACTOR"
    )
    max_promotion_drawdown_percent: float = Field(
        default=20, alias="MAX_PROMOTION_DRAWDOWN_PERCENT"
    )
    max_promotion_consecutive_losses: int = Field(
        default=8, alias="MAX_PROMOTION_CONSECUTIVE_LOSSES"
    )
    optimizer_max_combinations: int = Field(
        default=100, alias="OPTIMIZER_MAX_COMBINATIONS"
    )
    optimizer_sort_metric: str = Field(
        default="profit_factor", alias="OPTIMIZER_SORT_METRIC"
    )

    billing_enabled: bool = Field(default=True, alias="BILLING_ENABLED")
    billing_provider: str = Field(default="mock", alias="BILLING_PROVIDER")
    billing_currency: str = Field(default="USD", alias="BILLING_CURRENCY")
    billing_trial_days: int = Field(default=14, alias="BILLING_TRIAL_DAYS")
    billing_grace_period_days: int = Field(default=7, alias="BILLING_GRACE_PERIOD_DAYS")
    billing_webhook_secret: str = Field(default="", alias="BILLING_WEBHOOK_SECRET")
    billing_fail_closed: bool = Field(default=True, alias="BILLING_FAIL_CLOSED")

    # Usage Metering and Quotas
    usage_metering_enabled: bool = Field(default=True, alias="USAGE_METERING_ENABLED")
    usage_enforcement_enabled: bool = Field(default=True, alias="USAGE_ENFORCEMENT_ENABLED")
    usage_reset_mode: str = Field(default="monthly", alias="USAGE_RESET_MODE")

    stripe_enabled: bool = Field(default=False, alias="STRIPE_ENABLED")
    stripe_secret_key: str = Field(default="", alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", alias="STRIPE_WEBHOOK_SECRET")
    stripe_price_starter: str = Field(default="", alias="STRIPE_PRICE_STARTER")
    stripe_price_pro: str = Field(default="", alias="STRIPE_PRICE_PRO")
    stripe_price_enterprise: str = Field(default="", alias="STRIPE_PRICE_ENTERPRISE")

    usage_metering_enabled: bool = Field(default=True, alias="USAGE_METERING_ENABLED")
    usage_enforcement_enabled: bool = Field(default=True, alias="USAGE_ENFORCEMENT_ENABLED")
    usage_reset_mode: str = Field(default="monthly", alias="USAGE_RESET_MODE")

    marketplace_enabled: bool = Field(default=True, alias="MARKETPLACE_ENABLED")
    marketplace_install_enabled: bool = Field(default=True, alias="MARKETPLACE_INSTALL_ENABLED")
    marketplace_review_required: bool = Field(default=True, alias="MARKETPLACE_REVIEW_REQUIRED")
    plugin_runtime_mode: str = Field(default="sandbox", alias="PLUGIN_RUNTIME_MODE")
    plugin_allow_external_network: bool = Field(default=False, alias="PLUGIN_ALLOW_EXTERNAL_NETWORK")
    plugin_allow_secret_access: bool = Field(default=False, alias="PLUGIN_ALLOW_SECRET_ACCESS")

    enterprise_license_enabled: bool = Field(default=True, alias="ENTERPRISE_LICENSE_ENABLED")
    enterprise_offline_license_enabled: bool = Field(default=True, alias="ENTERPRISE_OFFLINE_LICENSE_ENABLED")
    enterprise_export_enabled: bool = Field(default=True, alias="ENTERPRISE_EXPORT_ENABLED")
    enterprise_import_enabled: bool = Field(default=True, alias="ENTERPRISE_IMPORT_ENABLED")

    white_label_enabled: bool = Field(default=True, alias="WHITE_LABEL_ENABLED")
    default_brand_name: str = Field(default="zDash", alias="DEFAULT_BRAND_NAME")
    default_brand_logo_url: str = Field(default="", alias="DEFAULT_BRAND_LOGO_URL")
    default_brand_primary_color: str = Field(default="#7c3aed", alias="DEFAULT_BRAND_PRIMARY_COLOR")
    default_brand_accent_color: str = Field(default="#22c55e", alias="DEFAULT_BRAND_ACCENT_COLOR")

    onboarding_enabled: bool = Field(default=True, alias="ONBOARDING_ENABLED")
    customer_success_enabled: bool = Field(default=True, alias="CUSTOMER_SUCCESS_ENABLED")

    frontend_origin: str = Field(
        default="http://localhost:5173", alias="FRONTEND_ORIGIN"
    )

    mobile_api_enabled: bool = Field(default=True, alias="MOBILE_API_ENABLED")
    developer_platform_enabled: bool = Field(
        default=True, alias="DEVELOPER_PLATFORM_ENABLED"
    )
    partner_api_enabled: bool = Field(default=True, alias="PARTNER_API_ENABLED")
    api_key_hash_pepper: str = Field(
        default="change-me-api-key-pepper", alias="API_KEY_HASH_PEPPER"
    )
    api_key_prefix: str = Field(default="zdash", alias="API_KEY_PREFIX")
    api_key_default_expires_days: int = Field(
        default=365, alias="API_KEY_DEFAULT_EXPIRES_DAYS"
    )

    digital_twin_enabled: bool = Field(default=True, alias="DIGITAL_TWIN_ENABLED")
    digital_twin_mode: str = Field(default="advisory", alias="DIGITAL_TWIN_MODE")
    digital_twin_dry_run: bool = Field(default=True, alias="DIGITAL_TWIN_DRY_RUN")
    digital_twin_require_evidence: bool = Field(
        default=True, alias="DIGITAL_TWIN_REQUIRE_EVIDENCE"
    )
    digital_twin_max_graph_nodes: int = Field(
        default=5000, alias="DIGITAL_TWIN_MAX_GRAPH_NODES"
    )
    digital_twin_max_graph_edges: int = Field(
        default=20000, alias="DIGITAL_TWIN_MAX_GRAPH_EDGES"
    )

    cors_allow_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ALLOW_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=False, alias="CORS_ALLOW_CREDENTIALS")

    @field_validator(
        "max_daily_drawdown_percent",
        "max_total_drawdown_percent",
        "emergency_kill_switch_drawdown_percent",
        "soft_halt_drawdown_level_1",
        "soft_halt_drawdown_level_2",
        "soft_halt_drawdown_level_3",
        mode="before",
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

    @field_validator(
        "backtest_initial_balance",
        "backtest_default_risk_per_trade_percent",
        "min_promotion_win_rate",
        "min_promotion_profit_factor",
        "max_promotion_drawdown_percent",
        mode="before",
    )
    @classmethod
    def _safe_positive_backtesting_float(cls, value):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.0
        if parsed < 0:
            return 0.0
        return parsed

    @field_validator(
        "backtest_commission_per_trade",
        "backtest_spread_points",
        "backtest_slippage_points",
        mode="before",
    )
    @classmethod
    def _safe_non_negative_backtesting_cost(cls, value):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.0
        if parsed < 0:
            return 0.0
        return parsed

    @field_validator(
        "min_promotion_trades",
        "max_promotion_consecutive_losses",
        "optimizer_max_combinations",
        mode="before",
    )
    @classmethod
    def _safe_positive_backtesting_int(cls, value):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        if parsed < 0:
            return 0
        return parsed

    @field_validator("db_pool_size", "db_max_overflow", mode="before")
    @classmethod
    def _safe_non_negative_db_pool(cls, value):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        if parsed < 0:
            return 0
        return parsed

    @field_validator(
        "jwt_access_token_expire_minutes",
        "jwt_refresh_token_expire_days",
        mode="before",
    )
    @classmethod
    def _safe_positive_auth_ttl(cls, value):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 1
        if parsed <= 0:
            return 1
        return parsed

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_allow_origins.split(",")]
        cleaned = [origin for origin in origins if origin]
        return cleaned or ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    default_unsafe_secret = "dev-only-change-before-production"

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

    # Backtesting safe defaults and bounds.
    if settings.backtest_initial_balance <= 0:
        settings.backtest_initial_balance = 10000.0
    if settings.backtest_default_risk_per_trade_percent <= 0:
        settings.backtest_default_risk_per_trade_percent = 1.0
    if settings.min_promotion_trades <= 0:
        settings.min_promotion_trades = 50
    if settings.min_promotion_win_rate <= 0:
        settings.min_promotion_win_rate = 45.0
    if settings.min_promotion_win_rate > 100:
        settings.min_promotion_win_rate = 100.0
    if settings.min_promotion_profit_factor <= 0:
        settings.min_promotion_profit_factor = 1.2
    if settings.max_promotion_drawdown_percent <= 0:
        settings.max_promotion_drawdown_percent = 20.0
    if settings.max_promotion_consecutive_losses <= 0:
        settings.max_promotion_consecutive_losses = 8
    if settings.optimizer_max_combinations <= 0:
        settings.optimizer_max_combinations = 100
    if settings.optimizer_max_combinations > 1000:
        settings.optimizer_max_combinations = 1000
    if settings.optimizer_sort_metric not in {
        "profit_factor",
        "net_profit_percent",
        "win_rate",
        "expectancy",
        "sharpe_like_score",
    }:
        settings.optimizer_sort_metric = "profit_factor"

    # Content pipeline safety defaults.
    if not settings.content_store.strip():
        settings.content_store = "in_memory"
    if settings.content_store not in {"in_memory"}:
        settings.content_store = "in_memory"
    if not settings.content_default_brand.strip():
        settings.content_default_brand = "zDash"
    if not settings.content_default_language.strip():
        settings.content_default_language = "en"
    if not settings.content_default_tone.strip():
        settings.content_default_tone = "professional"
    if not settings.image_generation_provider.strip():
        settings.image_generation_provider = "mock"
    if not settings.social_provider.strip():
        settings.social_provider = "mock"
    if not settings.social_default_platforms.strip():
        settings.social_default_platforms = "x,tiktok,facebook,instagram,linkedin"

    if settings.db_pool_size <= 0:
        settings.db_pool_size = 5
    if settings.db_max_overflow < 0:
        settings.db_max_overflow = 10
    if settings.jwt_access_token_expire_minutes <= 0:
        settings.jwt_access_token_expire_minutes = 60
    if settings.jwt_refresh_token_expire_days <= 0:
        settings.jwt_refresh_token_expire_days = 7

    ordered = sorted(
        [
            settings.soft_halt_drawdown_level_1,
            settings.soft_halt_drawdown_level_2,
            settings.soft_halt_drawdown_level_3,
        ]
    )
    (
        settings.soft_halt_drawdown_level_1,
        settings.soft_halt_drawdown_level_2,
        settings.soft_halt_drawdown_level_3,
    ) = ordered

    if settings.is_production:
        database_url = settings.database_url.strip()
        if not settings.production_safety_lock:
            if not settings.production_allow_live_actions:
                raise RuntimeError(
                    "PRODUCTION_SAFETY_LOCK can be disabled only with explicit PRODUCTION_ALLOW_LIVE_ACTIONS=true."
                )
        if not database_url:
            raise RuntimeError("DATABASE_URL is required in production mode.")
        if not database_url.startswith(
            (
                "postgres://",
                "postgresql://",
                "postgresql+psycopg://",
                "postgresql+psycopg2://",
            )
        ):
            raise RuntimeError(
                "DATABASE_URL must use PostgreSQL in production mode."
            )
        if settings.jwt_secret_key.strip() in {"", default_unsafe_secret}:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a non-default value in production mode."
            )
        if settings.bootstrap_admin_password.strip() in {"", default_unsafe_secret}:
            raise RuntimeError(
                "BOOTSTRAP_ADMIN_PASSWORD must be set to a non-default value in production mode."
            )
        if settings.default_admin_password.strip() in {"", default_unsafe_secret}:
            raise RuntimeError(
                "DEFAULT_ADMIN_PASSWORD must be set to a non-default value in production mode."
            )
    return settings

settings = get_settings()

