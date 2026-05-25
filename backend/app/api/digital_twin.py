from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.core.responses import ok, fail
from app.digital_twin.models import TwinEntity, TwinRelationship
from app.digital_twin.entity_registry import EntityRegistry
from app.digital_twin.relationship_service import RelationshipService
from app.digital_twin.twin_graph import TwinGraphService
from app.digital_twin.propagation_engine import PropagationEngine
from app.digital_twin.blast_radius import BlastRadiusService
from app.digital_twin.twin_snapshot_service import TwinSnapshotService
from app.digital_twin.twin_report_service import TwinReportService

router = APIRouter(prefix='/api/digital-twin', tags=['digital-twin'])
_registry=EntityRegistry(); _rels=RelationshipService(); _graph=TwinGraphService(_registry,_rels)
_prop=PropagationEngine(_graph); _blast=BlastRadiusService(_graph); _snap=TwinSnapshotService(_graph); _report=TwinReportService(_snap)

def _org_ws(): return 'org-default','ws-default'

@router.get('/status')
def status():
    s=get_settings();
    if not getattr(s,'digital_twin_enabled',True): return fail('DIGITAL_TWIN_DISABLED','Digital twin is disabled')
    return ok({'enabled':True,'mode':'advisory','dry_run':True})

@router.post('/entities')
def create_entity(entity:TwinEntity): return ok(_registry.create_entity(entity).model_dump())
@router.get('/entities')
def list_entities(): o,w=_org_ws(); return ok({'items':[e.model_dump() for e in _registry.list_entities(o,w)]})
@router.get('/entities/{entity_id}')
def get_entity(entity_id:str): o,w=_org_ws(); e=_registry.get_entity(o,w,entity_id); return ok(e.model_dump()) if e else fail('TWIN_ENTITY_NOT_FOUND','Entity not found')
@router.patch('/entities/{entity_id}')
def patch_entity(entity_id:str, patch:dict): o,w=_org_ws(); e=_registry.update_entity(o,w,entity_id,patch); return ok(e.model_dump()) if e else fail('TWIN_ENTITY_NOT_FOUND','Entity not found')
@router.post('/relationships')
def create_rel(rel:TwinRelationship): return ok(_rels.create_relationship(rel).model_dump())
@router.get('/relationships')
def list_rel(): o,w=_org_ws(); return ok({'items':[r.model_dump() for r in _rels.list_relationships(o,w)]})
@router.delete('/relationships/{relationship_id}')
def del_rel(relationship_id:str): o,w=_org_ws(); return ok({'deleted':_rels.delete_relationship(o,w,relationship_id)})
@router.get('/graph')
def graph(): o,w=_org_ws(); return ok(_graph.build_graph(o,w))
@router.get('/graph/summary')
def graph_summary(): o,w=_org_ws(); return ok(_graph.summarize_graph(o,w))
@router.get('/graph/neighbors/{entity_id}')
def neighbors(entity_id:str): o,w=_org_ws(); return ok({'items':[n.model_dump() for n in _graph.get_neighbors(o,w,entity_id)]})
@router.post('/impact/simulate')
def impact(body:dict): o,w=_org_ws(); return ok(_prop.simulate_impact(o,w,body['source_entity_id'],body.get('impact_type','generic'),body.get('assumptions',[])).model_dump())
@router.get('/impact/results')
def impact_results(): o,w=_org_ws(); return ok({'items':[r.model_dump() for r in _prop.list_propagation_results(o,w)]})
@router.post('/blast-radius/analyze')
def blast(body:dict): o,w=_org_ws(); return ok(_blast.analyze_blast_radius(o,w,body['target_entity_id'],body.get('severity','medium')).model_dump())
@router.get('/blast-radius/results')
def blast_results(): o,w=_org_ws(); return ok({'items':[r.model_dump() for r in _blast.list_blast_radius_results(o,w)]})
@router.post('/snapshots')
def snapshot(body:dict): o,w=_org_ws(); return ok(_snap.create_snapshot(o,w,body.get('name','snapshot')).model_dump())
@router.get('/snapshots')
def snapshots(): o,w=_org_ws(); return ok({'items':[s.model_dump() for s in _snap.list_snapshots(o,w)]})
@router.post('/reports')
def reports(body:dict): o,w=_org_ws(); return ok(_report.generate_twin_report(o,w,body.get('name','report')))
@router.get('/reports')
def reports_list(): o,w=_org_ws(); return ok({'items':_report.list_reports(o,w)})
@router.get('/reports/{report_id}/markdown')
def report_md(report_id:str): o,w=_org_ws(); r=next((x for x in _report.list_reports(o,w) if x['id']==report_id),None); return ok({'markdown':_report.build_markdown_report(r)}) if r else fail('SCENARIO_PACK_NOT_FOUND','Report not found')
