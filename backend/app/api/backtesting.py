from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.backtesting.optimizer import Optimizer
from app.backtesting.reports import selection_report
from app.backtesting.strategy_lab import STRATEGY_MAP, StrategyLab
from app.core.auth import CurrentUser, require_roles
from app.core.config import get_settings
from app.core.database import session_scope
from app.core.responses import fail, ok
from app.repositories import Repository

router = APIRouter(prefix='/api/backtesting', tags=['backtesting'])

settings = get_settings()
lab = StrategyLab()
optimizer = Optimizer()


class BacktestRunRequest(BaseModel):
    strategy: str = Field(default='ob_aggressive')
    risk_per_trade: float = Field(default=1.0, gt=0)


class OptimizeRequest(BaseModel):
    strategy: str = Field(default='ob_aggressive')
    risks: list[float] = Field(default=[0.5, 1.0, 1.5])


@router.post('/run')
def run_backtest(req: BacktestRunRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    if req.strategy not in STRATEGY_MAP:
        return fail('STRATEGY_NOT_FOUND', f'Unknown strategy: {req.strategy}')
    result = lab.run(req.strategy, req.risk_per_trade)
    result['promotion_allowed'] = result['max_drawdown'] < settings.max_total_drawdown_percent
    result['selection_note'] = selection_report(req.strategy, result)
    with session_scope() as session:
        repo = Repository(session)
        run = repo.add_backtest_run(req.strategy, req.risk_per_trade, req.strategy == settings.primary_strategy)
        repo.add_backtest_result(run.id, result)
    return ok({'result': result})


@router.get('/results')
def get_results(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    with session_scope() as session:
        rows = Repository(session).list_backtest_results()
    results = [
        {
            'id': r.id,
            'run_id': r.run_id,
            'metrics': r.metrics,
            'created_at': r.created_at.isoformat(),
        }
        for r in rows
    ]
    return ok({'results': results})


@router.post('/optimize')
def optimize(req: OptimizeRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    if req.strategy not in STRATEGY_MAP:
        return fail('STRATEGY_NOT_FOUND', f'Unknown strategy: {req.strategy}')
    rows = optimizer.sweep(req.strategy, req.risks)
    return ok({'ranked_results': rows})


@router.get('/strategies')
def list_strategies(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'strategies': list(STRATEGY_MAP.keys()), 'primary_strategy': settings.primary_strategy})
