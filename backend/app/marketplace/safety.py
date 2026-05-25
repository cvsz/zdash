def check_plugin_action(action:str,payload:dict|None=None):
    lowered=action.lower()
    blocked=['live_trade','real_iot','real_social']
    if any(b in lowered for b in blocked): return False,'PLUGIN_SAFETY_BLOCKED'
    return True,'ok'
