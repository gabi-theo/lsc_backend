from django.db.models import Q

from recuperari.models import MakeUp


class MakeUpService:
    @staticmethod
    def get_make_ups_for_school_by_session(school, session):
        return MakeUp.objects.filter(
            make_up_for_session__course_session__course__school=school,
            make_up_for_session__session_no=session.session_no,
        )

    @staticmethod
    def get_make_ups_excluding_current_school_by_session(school, session):
        return MakeUp.objects.filter(
            Q(make_up_for_session__course_session__course_type__in=["onl", "hbr"]) &
            Q(make_up_for_session__session_no=session.session_no) &
            ~Q(make_up_for_session__course_session__course__school=school)
        )

    @staticmethod
    def get_makeups_by_user_school(user):
        return MakeUp.objects.filter(make_up_for_session__course_session__course__school__user=user)

    @staticmethod
    def get_make_up_for_student_by_session(student, session):
        return MakeUp.objects.filter(make_up_for_session=session, students__in=[student])

    @classmethod
    def create_empty_make_up_session_for_student(cls, student, session):
        # first check that student is not in any make_up group for this session
        
        if not cls.get_make_up_for_student_by_session(student, session).exists():
            make_up = MakeUp.objects.create(
                make_up_for_session=session,
            )
            make_up.students.add(student)
