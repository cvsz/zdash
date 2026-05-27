from app.collaboration.service import CollaborationService
from app.collaboration.schemas import PresenceUpdate

def test_presence_lifecycle():
    s=CollaborationService()
    s.upsert_presence('u1', PresenceUpdate(workspace_id='w1', session_id='s1', state='online'))
    assert len(s.list_presence('w1')) == 1
