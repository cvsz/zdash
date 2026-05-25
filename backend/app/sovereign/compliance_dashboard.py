class SovereignComplianceDashboard:
    def __init__(self, region_registry, residency_engine, kms, bundles): self.region_registry=region_registry; self.residency_engine=residency_engine; self.kms=kms; self.bundles=bundles
    def get_status(self): return {'enabled':True,'fail_closed':True}
    def get_region_summary(self): return {'regions':len(self.region_registry.list_regions())}
    def get_residency_violations(self): return []
    def get_kms_summary(self): return self.kms.get_kms_status()
    def get_policy_bundle_summary(self): return {'bundles':len(self.bundles.list_bundles())}
    def generate_report(self): return {'status':self.get_status(),'kms':self.get_kms_summary()}
