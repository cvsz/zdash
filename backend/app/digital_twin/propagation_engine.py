from .models import ImpactPropagationResult
class PropagationEngine:
    def __init__(self,graph): self.graph=graph; self._results=[]
    def simulate_impact(self,org,ws,source_entity_id,impact_type,assumptions):
        affected=[{'entity_id':getattr(r,'target_entity_id',None),'score':getattr(r,'weight',1.0)} for r in self.graph.get_neighbors(org,ws,source_entity_id)]
        out=ImpactPropagationResult(id=f'ipr-{len(self._results)+1}',organization_id=org,workspace_id=ws,source_entity_id=source_entity_id,impact_type=impact_type,affected_entities=affected,impact_score=sum(x['score'] for x in affected),confidence=0.6,assumptions=assumptions,limitations=['simulation-only'])
        self._results.append(out); return out
    def rank_affected_entities(self,result): return sorted(result.affected_entities,key=lambda x:x.get('score',0),reverse=True)
    def list_propagation_results(self,org,ws): return [r for r in self._results if r.organization_id==org and r.workspace_id==ws]
