from .models import RegionRecord, DataRegion
class RegionRegistry:
    def __init__(self):
        self._regions={r.value:RegionRecord(id=r.value,code=r,name=r.value.upper(),jurisdiction='default',allowed=True) for r in [DataRegion.local,DataRegion.us,DataRegion.eu,DataRegion.apac]}
    def list_regions(self): return list(self._regions.values())
    def get_region(self, region_code:str): return self._regions.get(region_code)
    def register_region(self, region:RegionRecord): self._regions[region.code.value]=region; return region
    def update_region_status(self, region_code:str, allowed:bool): r=self._regions[region_code]; r.allowed=allowed; return r
    def is_region_allowed(self, region_code:str): r=self.get_region(region_code); return bool(r and r.allowed)
