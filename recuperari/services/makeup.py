from django.db.models import Q

from recuperari.models import (
    MakeUp,
)


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
