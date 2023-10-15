from recuperari.models import User
from typing import Optional


class UserService:
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        return User.objects.filter(username=username).first()
