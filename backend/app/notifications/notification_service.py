from .channels import sanitize_payload
EVENTS=[]

def send_notification(title,message,payload,dry_run=True):
    rec={"title":title,"message":message,"payload":sanitize_payload(payload),"dry_run":dry_run}
    EVENTS.append(rec)
    return rec
