from .builtins import BUILTINS

def list_plugins(): return BUILTINS
def get_plugin(plugin_id:str): return next((p for p in BUILTINS if p.id==plugin_id),None)
