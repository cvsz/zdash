import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.agents.registry import bootstrap_agents
from app.api import (
    admin,
    agents,
    auth,
    backtesting,
    billing,
    content,
    enterprise,
    health,
    iot,
    logs,
    marketplace,
    metrics,
    risk,
    scheduler,
    trading,
    ops,
    integrations,
    managed,
    developer,
    partner,
    mobile,
    launch,
    predictive_sre,
    digital_twin,
    macro_simulation,
    continuous_planning,
    enterprise_os,
    self_evolution,
    governance_refinement,
    long_horizon,
    lessons,
)
from app.core.config import get_settings
from app.core.events import event_bus
from app.core.logging import configure_logging
from app.core.responses import fail
from app.db.migrations import run_migrations
from app.observability.middleware import install_observability_middleware
from app.scheduler.scheduler_service import get_scheduler_service

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_migrations()
    bootstrap_agents()
    scheduler_service = get_scheduler_service()
    scheduler_service.start()
    event_bus.emit(
        "system.startup",
        "app.main",
        "FastAPI startup complete",
        {
            "backtesting_enabled": settings.backtesting_enabled,
            "primary_strategy_candidate": settings.primary_strategy,
            "strategy_promotion_enabled": settings.allow_strategy_promotion,
            "content_pipeline_enabled": settings.content_pipeline_enabled,
            "social_dry_run": settings.social_dry_run,
            "social_approval_required": settings.social_approval_required,
        },
    )
    yield
    scheduler_service.stop()


app = FastAPI(title="Janie Server", version="2.0.0-phase8.3", lifespan=lifespan)

origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_observability_middleware(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "validation_error",
        extra={"context": {"path": request.url.path, "error": str(exc)}},
    )
    return JSONResponse(status_code=422, content=fail("VALIDATION_ERROR", str(exc)))


app.include_router(health.router)
app.include_router(agents.router)
app.include_router(logs.router)
app.include_router(risk.router)
app.include_router(trading.router)

app.include_router(scheduler.router)
app.include_router(iot.router)

app.include_router(backtesting.router)

app.include_router(content.router)

app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(admin.router)

app.include_router(billing.router)
app.include_router(marketplace.router)
app.include_router(enterprise.router)
app.include_router(ops.router)
app.include_router(integrations.router)
app.include_router(managed.router)

app.include_router(developer.router)
app.include_router(partner.router)
app.include_router(mobile.router)

app.include_router(launch.router)

app.include_router(predictive_sre.router)

app.include_router(digital_twin.router)
app.include_router(macro_simulation.router)
app.include_router(continuous_planning.router)

app.include_router(enterprise_os.router)
app.include_router(self_evolution.router)
app.include_router(governance_refinement.router)
app.include_router(long_horizon.router)
app.include_router(lessons.router)
