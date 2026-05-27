STEPS=['create organization','create workspace','invite team','verify risk guardian','run first dry-run scan','run first backtest','create first content item','review scheduler jobs','configure billing','review production safety check']
_STATE: dict[tuple[str, str], list[str]] = {}
def get_checklist(organization_id,workspace_id):
    c=_STATE.get((organization_id,workspace_id),[]); return {'completed_steps':c,'pending_steps':[s for s in STEPS if s not in c],'progress_percent':int((len(c)/len(STEPS))*100)}
def mark_step_complete(organization_id,workspace_id,step): c=_STATE.setdefault((organization_id,workspace_id),[]); c.append(step) if step not in c else None; return get_checklist(organization_id,workspace_id)
def reset_checklist(organization_id,workspace_id): _STATE[(organization_id,workspace_id)]=[]; return get_checklist(organization_id,workspace_id)
def get_customer_health(organization_id,workspace_id): c=get_checklist(organization_id,workspace_id); return {'score':c['progress_percent']}
