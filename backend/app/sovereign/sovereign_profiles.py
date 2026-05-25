from .models import SovereignDeploymentProfile, SovereignProfileStatus
class SovereignProfileService:
    def __init__(self): self._profiles=[]
    def create_profile(self,p): self._profiles.append(p); return p
    def list_profiles(self): return self._profiles
    def activate_profile(self,pid):
        for p in self._profiles: p.status=SovereignProfileStatus.active if p.id==pid else p.status
        return self.get_active_profile()
    def disable_profile(self,pid):
        for p in self._profiles:
            if p.id==pid: p.status=SovereignProfileStatus.disabled; return p
    def get_active_profile(self): return next((p for p in self._profiles if p.status==SovereignProfileStatus.active), None)
    def validate_profile(self,p): return p.data_region is not None
