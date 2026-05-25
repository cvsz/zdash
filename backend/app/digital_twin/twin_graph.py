class TwinGraphService:
    def __init__(self,registry,rels,max_nodes=5000,max_edges=20000): self.registry=registry; self.rels=rels; self.max_nodes=max_nodes; self.max_edges=max_edges
    def build_graph(self,org,ws):
        n=self.registry.list_entities(org,ws); e=self.rels.list_relationships(org,ws)
        if len(n)>self.max_nodes or len(e)>self.max_edges: raise ValueError('TWIN_GRAPH_LIMIT_EXCEEDED')
        return {'nodes':[x.model_dump() for x in n],'edges':[x.model_dump() for x in e]}
    def get_neighbors(self,org,ws,entity_id):
        return [r for r in self.rels.list_relationships(org,ws) if r.source_entity_id==entity_id or r.target_entity_id==entity_id]
    def get_dependency_path(self,org,ws,source_id,target_id): return [source_id,target_id] if self.get_neighbors(org,ws,source_id) else []
    def summarize_graph(self,org,ws): g=self.build_graph(org,ws); return {'node_count':len(g['nodes']),'edge_count':len(g['edges'])}
    def detect_orphans(self,org,ws):
        ids={e.id for e in self.registry.list_entities(org,ws)}; linked=set()
        for r in self.rels.list_relationships(org,ws): linked.add(r.source_entity_id); linked.add(r.target_entity_id)
        return sorted(ids-linked)
    def detect_cycles(self,org,ws):
        return [r.id for r in self.rels.list_relationships(org,ws) if r.source_entity_id==r.target_entity_id]
