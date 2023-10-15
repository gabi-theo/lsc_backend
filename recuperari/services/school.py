from recuperari.models import School
from typing import Optional
from .users import UserService
import uuid


class SchoolService:
    @staticmethod
    def create_school_with_user_by_username(username: str, school_name: str, phone_contact: str, email_contact: str, room_count: int) -> Optional[School]:
        user = UserService.get_user_by_username(username=username)
        if user is None:
            return None
        else:
            school = School.objects.create(
                user=user,
                name=school_name,
                phone_contact=phone_contact,
                email_contact=email_contact,
                room_count=room_count,
            )
            return school
