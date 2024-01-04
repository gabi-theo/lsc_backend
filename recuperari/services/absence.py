from recuperari.models import AbsentStudent

class AbsenceService:
    @staticmethod
    def create_absent_student_for_session(
        session,
        student
    ):
        return AbsentStudent.objects.get_or_create(
            absent_participant=student,
            absent_on_session=session
        )

    @staticmethod
    def get_all_absences_from_school(school):
        return AbsentStudent.objects.filter(
            absent_on_session__course_session__school=school)

    @staticmethod
    def get_absence_by_id(absence_id):
        return AbsentStudent.objects.filter(pk=absence_id).first()
