from fastapi import APIRouter
router=APIRouter(prefix='/api/global-ops',tags=['global-ops'])
@router.get('/status')
def status(): return {'ok':True,'data':{'enabled':True,'dry_run':True},'error':None}
