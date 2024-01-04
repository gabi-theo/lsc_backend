from django.core.serializers import serialize
from datetime import datetime
from recuperari.models import AbsentStudent, MakeUp
from recuperari.utils import create_serialized_response_from_object


class MakeUpService:
    @staticmethod
    def get_make_up_by_id(pk):
        return MakeUp.objects.filter(pk=pk).first()

    @staticmethod
    def get_make_ups_for_session(absence: AbsentStudent, school):
        available_sessions = []
        fields_to_include_for_serializer = [
            "session__id",
            "session__session_no",
            "trainer",
            "date_time",
            "session__course_session__school__name",
            "online_link"]
        absence_session = absence.absent_on_session
        is_absence_possible_online = absence_session.course_session.course_type != "sed"

        matching_sessions = MakeUp.objects.filter(
            session__session_no=absence_session.session_no,
            session__course_session__course = absence_session.course_session.course,
            date_time__gte=datetime.now()
        ).exclude(id=absence_session.id).order_by("date_time")

        school_sessions = matching_sessions.filter(
            session__course_session__school=school,
        )
        print(school_sessions)
        if is_absence_possible_online:
            other_school_sessions = matching_sessions.exclude(
                id__in=school_sessions,
            ).filter(session__course_session__can_be_used_as_online_make_up_for_other_schools=True)
            print(other_school_sessions)
            for session in other_school_sessions:
                if (
                    session.make_up_absences.all().count() <
                    session.available_places_for_make_up_for_other_schools
                ):
                    available_sessions.append(
                        create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))

        for session in school_sessions:
            if (
                session.make_up_absences.all().count() <
                session.available_places_for_make_up_for_current_school
            ):
                available_sessions.append(
                    create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))

        return available_sessions


    @staticmethod
    def get_makeups_by_user_school(user):
        return MakeUp.objects.filter(make_up_for_absence__absent_on_session__course_session__school__user=user)

    @staticmethod
    def get_make_up_for_student_by_session(student, session):
        return MakeUp.objects.filter(make_up_for_absence__absent_on_session=session, students__in=[student])

    @classmethod
    def create_empty_make_up_session_for_absence(cls, student, absence):
        # first check that student is not in any make_up group for this session
        
        if not cls.get_make_up_for_student_by_session(student, absence).exists():
            make_up = MakeUp.objects.create(
                make_up_for_absence=absence,
            )
            make_up.students.add(student)
