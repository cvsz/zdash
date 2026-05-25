from .models import PolicyBundle
class PolicyBundleService:
    def __init__(self): self._bundles=[]
    def create_bundle(self,b): self._bundles.append(b); return b
    def list_bundles(self): return self._bundles
    def get_bundle(self,bid): return next((b for b in self._bundles if b.id==bid), None)
    def export_bundle(self,bid): return self.get_bundle(bid)
