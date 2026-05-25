from app.auth.password import verify_password
from app.auth.jwt import create_access_token
from app.db.repositories import UserRepository

class AuthService:
    def __init__(self, users: UserRepository): self.users = users
    def login(self, email: str, password: str):
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash): return None
        return create_access_token(user.email, user.role)
