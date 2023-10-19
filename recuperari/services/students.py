import pandas as pd

from recuperari.models import Student, User
from recuperari.tasks import send_students_email
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

    @staticmethod
    def create_user_for_student(
        username,
        password,
    ):
        return User.objects.create_user(
            username=username,
            password=password,
            is_reset_password_needed=True,
            role="trainer",
        )

    @staticmethod
    def send_emails_to_students_in_groups(groups:str, subject:str, message:str):
        groups = groups.split(",")
        for group_pk in groups:
            student_emails = []
            group_students = CourseService.get_students_from_course_schedule(group_pk)
            for student in group_students:
                student_emails.append(student.parent_email)
            send_students_email.delay(
                student_emails,
                message,
                subject,
            )

    @classmethod
    def send_whatsapp_to_students_in_groups(cls, groups:str, subject:str, message:str):
        pass
