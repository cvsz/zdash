from fastapi import APIRouter, Depends, Header
from app.core.responses import ok
from app.core.auth import get_current_user
from app.enterprise.license_service import get_license_status,apply_license,revoke_license
from app.enterprise.branding_service import get_branding,update_branding,reset_branding
from app.enterprise.export_service import list_export_bundles,create_export_bundle,get_export_bundle
from app.enterprise.onboarding_service import get_checklist,mark_step_complete,reset_checklist,get_customer_health
router=APIRouter(prefix='/api/enterprise',tags=['enterprise'])
def _org(o): return o or 'default-org'
def _ws(w): return w or 'default'
@router.get('/status')
def status(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok({'license':get_license_status(_org(x_organization_id)),'branding':get_branding(_org(x_organization_id),_ws(x_workspace_id))})
@router.get('/license')
def license_status(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(get_license_status(_org(x_organization_id)))
@router.post('/license/apply')
def license_apply(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(apply_license(_org(x_organization_id),body.get('license_key','')))
@router.post('/license/revoke')
def license_revoke(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(revoke_license(_org(x_organization_id)))
@router.get('/branding')
def branding(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(get_branding(_org(x_organization_id),_ws(x_workspace_id)))
@router.patch('/branding')
def branding_patch(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(update_branding(_org(x_organization_id),_ws(x_workspace_id),body))
@router.post('/branding/reset')
def branding_reset(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(reset_branding(_org(x_organization_id),_ws(x_workspace_id)))
@router.get('/exports')
def exports(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok({'exports':list_export_bundles(_org(x_organization_id))})
@router.post('/exports')
def create_export(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(create_export_bundle({'organization_id':_org(x_organization_id),'workspace_id':_ws(x_workspace_id),**body}))
@router.get('/exports/{bundle_id}')
def export_get(bundle_id:str,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(get_export_bundle(_org(x_organization_id),bundle_id))
@router.get('/onboarding')
def onboarding(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(get_checklist(_org(x_organization_id),_ws(x_workspace_id)))
@router.post('/onboarding/complete-step')
def onboarding_step(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(mark_step_complete(_org(x_organization_id),_ws(x_workspace_id),body.get('step','')))
@router.post('/onboarding/reset')
def onboarding_reset(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(reset_checklist(_org(x_organization_id),_ws(x_workspace_id)))
@router.get('/customer-health')
def health(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(get_customer_health(_org(x_organization_id),_ws(x_workspace_id)))
