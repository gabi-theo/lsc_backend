from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from recuperari.models import AbsentStudent, Session, SessionsDescription
from recuperari.utils import create_serialized_response_from_object


class SessionService:
    @staticmethod
    def get_session_by_id(session_id):
        try:
            return Session.objects.filter(pk=session_id)
        except Session.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_session_by_course_schedule_id(course_schedule_id):
        return Session.objects.filter(course_session__id=course_schedule_id)

    @staticmethod
    def get_session_description_by_course_id(course_id):
        return SessionsDescription.objects.filter(course=course_id)

    @staticmethod
    def get_sessions_by_user_school(user):
        return Session.objects.filter(course_session__school=user.user_school.all().first())

    @staticmethod
    def get_next_sessions_for_absence(absence: AbsentStudent, school):
        available_sessions = []
        fields_to_include_for_serializer = [
            "id",
            "course_session__id",
            "session_no",
            "session_trainer",
            "date",
            "course_session__time",
            "course_session__school__name",
            "course_session__online_link",
            "course_session__available_places_for_make_up_for_other_schools",
            "course_session__available_places_for_make_up_for_current_school"]
        absence_session = absence.absent_on_session
        is_absence_possible_online = absence_session.course_session.course_type != "sed"

        matching_sessions = Session.objects.filter(
            session_no=absence_session.session_no,
            course_session__course = absence_session.course_session.course,
            date__gte=datetime.now()
        ).exclude(id=absence_session.id).order_by("date")

        school_sessions = matching_sessions.filter(
            course_session__school=school,
        )
        # if is_absence_possible_online:
        other_school_sessions = matching_sessions.exclude(
            id__in=school_sessions,
        ).filter(course_session__can_be_used_as_online_make_up_for_other_schools=True)
        for session in other_school_sessions:
            if (
                session.course_session_absence.all().count() <
                session.course_session.available_places_for_make_up_for_other_schools
            ):
                available_sessions.append(
                    create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))
        for session in school_sessions:
            if (
                session.course_session_absence.all().count() <
                session.course_session.available_places_for_make_up_for_current_school
            ):
                available_sessions.append(
                    create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))
        return available_sessions
