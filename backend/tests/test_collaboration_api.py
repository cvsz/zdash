from app.auth.models import AuthSession
from app.collaboration.router import get_presence


def test_collab_presence_endpoint() -> None:
    response = get_presence(
        workspace_id="w1",
        _=AuthSession(username="dev-user", role="admin"),
    )
    assert response["ok"] is True
    assert response["error"] is None
    assert isinstance(response["data"]["items"], list)
