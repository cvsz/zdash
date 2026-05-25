import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.agents.registry import bootstrap_agents
from app.api import admin, agents, auth, backtesting, billing, content, enterprise, health, iot, logs, marketplace, metrics, risk, scheduler, ops, integrations, managed, developer, partner, mobile, launch
from app.core.config import get_settings
from app.core.events import event_bus
from app.core.logging import configure_logging
from app.core.responses import fail
from app.db.migrations import run_migrations

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_migrations()
    bootstrap_agents()
    event_bus.emit('system.startup', 'app.main', 'FastAPI startup complete', {})
    yield


app = FastAPI(title='Janie Server', version='2.0.0-phase7', lifespan=lifespan)

origins=[o.strip() for o in settings.cors_allow_origins.split(',') if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['*'], allow_headers=['*'])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning('validation_error', extra={'context': {'path': request.url.path, 'error': str(exc)}})
    return JSONResponse(status_code=422, content=fail('VALIDATION_ERROR', str(exc)))


@app.middleware('http')
async def request_log_middleware(request: Request, call_next):
    logger.info('request', extra={'context': {'method': request.method, 'path': request.url.path}})
    response = await call_next(request)
    return response


app.include_router(health.router)
app.include_router(agents.router)
app.include_router(logs.router)
app.include_router(risk.router)

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
