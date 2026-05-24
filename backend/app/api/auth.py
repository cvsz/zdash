import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import CurrentUser, create_access_token, get_current_user, verify_password
from app.core.database import get_session
from app.core.responses import fail, ok
from app.repositories import Repository

router = APIRouter(prefix='/api/auth', tags=['auth'])
_login_attempts: dict[str, deque[float]] = defaultdict(deque)
MAX_LOGIN_ATTEMPTS = 8
WINDOW_SECONDS = 300


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.post('/login')
def login(req: LoginRequest, session: Session = Depends(get_session)):
    now = time.time()
    bucket = _login_attempts[req.username]
    while bucket and now - bucket[0] > WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_LOGIN_ATTEMPTS:
        return fail('LOGIN_RATE_LIMITED', 'Too many login attempts. Try again later.')

    repo = Repository(session)
    user = repo.get_user_by_username(req.username)
    if user is None or not verify_password(req.password, user.password_hash):
        bucket.append(now)
        from app.core.observability import auth_login_total

        auth_login_total.labels(status='failure').inc()
        repo.add_audit_log('auth_login_failed', req.username, 'unknown', detail={'username': req.username})
        return fail('AUTH_FAILED', 'Invalid username or password')
    token = create_access_token(user.username, user.role)
    from app.core.observability import auth_login_total

    auth_login_total.labels(status='success').inc()
    if req.username in _login_attempts:
        _login_attempts[req.username].clear()
    repo.add_audit_log('auth_login_success', user.username, user.role, detail={})
    return ok({'access_token': token, 'token_type': 'bearer', 'role': user.role, 'username': user.username})


@router.get('/me')
def me(current_user: CurrentUser = Depends(get_current_user)):
    return ok({'username': current_user.username, 'role': current_user.role})
