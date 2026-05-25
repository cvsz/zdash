from fastapi import APIRouter
from app.core.responses import success_response
router=APIRouter(prefix='/api/integrations', tags=['integrations'])
@router.get('/status')
def status(): return success_response({'enabled':True,'dry_run':True})
@router.get('/catalog')
def catalog(): return success_response({'types':['webhook','siem','ticketing','sso','scim']})
