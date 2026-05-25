from fastapi import APIRouter
from app.core.responses import ok

router = APIRouter(prefix='/api/admin', tags=['admin'])

@router.get('/safety-check')
def safety_check():
    return ok({'status':'safe','warnings':[], 'blockers':[], 'score':100})

@router.get('/audit-logs')
def audit_logs():
    return ok([])

@router.get('/users')
def users():
    return ok([])
