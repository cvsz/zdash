from app.collaboration.service import CollaborationService

def test_timeline_replay():
    s=CollaborationService()
    s.add_event('w1','workspace.joined','u1','joined')
    items, cursor = s.list_timeline('w1',0,10)
    assert len(items)==1 and cursor==1
