from fastapi.testclient import TestClient
from app.main import app

def test_collab_presence_endpoint():
    c=TestClient(app)
    r=c.get('/api/collaboration/presence', params={'workspace_id':'w1'})
    assert r.status_code==200
