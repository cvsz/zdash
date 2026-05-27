from fastapi.testclient import TestClient

from app.main import app


def _token(client: TestClient, username: str, role: str):
    r = client.post('/api/auth/bootstrap-admin', json={'username': username, 'password': 'pw', 'role': role})
    return r.json()['data']['access_token']


def test_incident_rbac_flow():
    c = TestClient(app)
    viewer = _token(c, 'viewer_u', 'viewer')
    operator = _token(c, 'op_u', 'operator')
    admin = _token(c, 'admin_u2', 'admin')
    assert c.get('/api/incidents', headers={'Authorization': f'Bearer {viewer}'}).status_code == 200
    assert c.post('/api/incidents', json={'title':'x','severity':'warning'}, headers={'Authorization': f'Bearer {viewer}'}).status_code == 403
    created = c.post('/api/incidents', json={'title':'x','severity':'warning'}, headers={'Authorization': f'Bearer {operator}'}).json()['data']
    iid = created['id']
    assert c.post(f'/api/incidents/{iid}/ack', headers={'Authorization': f'Bearer {operator}'}).status_code == 200
    assert c.post(f'/api/incidents/{iid}/resolve', json={'notes':'done'}, headers={'Authorization': f'Bearer {operator}'}).status_code == 403
    assert c.post(f'/api/incidents/{iid}/resolve', json={'notes':'done'}, headers={'Authorization': f'Bearer {admin}'}).status_code == 200
