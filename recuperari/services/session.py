from rest_framework import status
from rest_framework.response import Response

from recuperari.models import Session, SessionsDescription


class SessionService:
    @staticmethod
    def get_session_by_id(session_id):
        try:
            return Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_session_by_course_schedule_id(course_schedule_id):
        return Session.objects.filter(course_session__id=course_schedule_id)

    @staticmethod
    def get_session_description_by_course_id(course_id):
        return SessionsDescription.objects.filter(course=course_id)
