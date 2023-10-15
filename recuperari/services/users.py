from recuperari.models import User
from typing import Optional


class UserService:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.objects.filter(email=email).first()
