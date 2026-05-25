from fastapi import APIRouter
from app.core.responses import ok
router=APIRouter(prefix='/api/macro-simulation',tags=['macro-simulation'])
@router.get('/status')
def status(): return ok({'enabled':True,'dry_run':True,'advisory':True})
