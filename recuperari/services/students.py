import pandas as pd

from recuperari.models import Student

from .course import CourseService


class StudentService:
    @staticmethod
    def create_student_from_excel_and_assign_it_to_school_course(
        excel_file,
        school,
    ):
        # Read the Excel file
        df = pd.read_excel(excel_file, skiprows=[0])
        # Loop through the rows and create CourseSchedule objects
        for _, row in df.iterrows():
            student, _ = Student.objects.get_or_create(
                school=school,
                participant_name=row["participant_fullName"],
                participant_parent_name=row["companion_fullName"],
                parent_phone_number=row["companion_phones"],
                parent_email=row["companion_emails"],
            )
            CourseService.add_student_to_course_schedule_by_group_name_day_and_time(
                student=student,
                group_name=row["group_name"],
                day=row['schedule_times'].split(" ")[0],
                time=row['schedule_times'].split(" ")[1],
            )

    @staticmethod
    def get_student_by_id(student_id):
        return Student.objects.filter(id=student_id).first()
