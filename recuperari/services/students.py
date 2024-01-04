import pandas as pd
from unidecode import unidecode
from recuperari.models import Student, StudentCourseSchedule, User, Parent
from recuperari.tasks import send_students_email, send_students_whatsapp
from .course import CourseService
from .whatsapp import WhatsappService


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
            if isinstance(row["companion_phones"],float):
                row["companion_phones"] = "Missing"
            if isinstance(row["companion_fullName"],float):
                row["companion_fullName"] = "Missing"
            if isinstance(row["companion_emails"],float):
                row["companion_emails"] = "Missing"
            parent, _ = Parent.objects.get_or_create(
                school=school,
                first_name=row["companion_fullName"].split(" ")[0],
                last_name=" ".join(row["companion_fullName"].split(" ")[1:]),
                phone_number1=row["companion_phones"].split(", ")[0],
                phone_number2=" ".join(row["companion_phones"].split(", ")[1:]),
                email1=row["companion_emails"].split(", ")[0],
                email2=" ".join(row["companion_emails"].split(", ")[1:]),
            )
            student, _ = Student.objects.get_or_create(
                parent=parent,
                first_name=row["participant_fullName"].split(" ")[0],
                last_name=" ".join(row["participant_fullName"].split(" ")[1:]),
            )
            CourseService.add_student_to_course_schedule_by_group_name_day_and_time(
                student=student,
                group_name=row["group_name"],
                day=unidecode(row['schedule_times'].split(" ")[0]),
                time=row['schedule_times'].split(" ")[1],
            )

    @staticmethod
    def get_student_by_name_and_email(name, email):
        return Student.objects.get(participant_name=name, parent_email=email)

    @classmethod
    def add_student_start_day_of_course(cls, excel_file, school):
        df = pd.read_excel(excel_file, skiprows=[0])
        grouped = df.groupby(['person_fullName', "person_id.parents_emails", 'group_name'])
        min_start_dates = grouped['timestamp'].min().reset_index()
        for _, row in min_start_dates.iterrows():
            print(f"{row['person_fullName']} - {row['group_name']}")
            try:
                student = cls.get_student_by_name_and_email(
                    name=row["person_fullName"],
                    email=row["person_id.parents_emails"])
                course_schedule = CourseService.get_course_schedule_by_group_name(
                    row["group_name"]
                )
                student_course_session = StudentCourseSchedule.objects.filter(
                    student=student,
                    course_schedule=course_schedule
                ).first()
                if student_course_session:
                    student_course_session.start_date = row["timestamp"].date()
                    student_course_session.save()
                else:
                    print(f"No timestamp for {row['person_fullName']} on group {row['group_name']}")
            except Exception as e:
                print(f"No timestamp for {row['person_fullName']} on group {row['group_name']}. Original error was: {e}")
                continue

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

    @classmethod
    def send_emails_to_students_in_groups(cls, groups:str, subject:str, message:str):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("SENDING MAILS TO:")
        groups_pks = groups.split(",")
        print(groups_pks)
        student_emails = []
        if len(groups_pks) == 1 and groups_pks[0] == "all":
            student_emails = cls.get_emails_from_all_active_students()
        else:
            student_emails = CourseService.get_emails_of_students_from_course_schedule_by_schedule_pks(
                        groups_pks)
        send_students_email.delay(
            student_emails,
            subject,
            message,
        )

    @classmethod
    def send_whatsapp_to_students_in_groups(cls, groups:str, message:str):
        groups_pks = groups.split(",")
        student_phones = []
        if len(groups_pks) == 1 and groups_pks[0] == "all":
            student_phones = cls.get_phone_numbers_from_all_active_students()
        else:
            student_phones = CourseService.get_phones_of_students_from_course_schedule_by_schedule_pks(
                        groups_pks)
        print(student_phones)
        for phone in student_phones:
            for number in phone.split(","):
                try:
                    # WhatsappService.send_whatsapp_message(recipient=phone, message=message)
                    send_students_whatsapp.delay(recipient=number, message=message)
                except Exception as e:
                    print(f"Couldn`t send message to {number}. Original error: {e}")

    @staticmethod
    def get_emails_from_all_active_students():
        return list(
            Student.objects.filter(
                student_active=True
            ).values_list('parent_email', flat=True).distinct())
    
    @staticmethod
    def get_phone_numbers_from_all_active_students():
        return list(
            Student.objects.filter(
                student_active=True
            ).values_list('parent_phone_number', flat=True).distinct())

    @staticmethod
    def get_students_first_day_of_course_by_school(school):
        return StudentCourseSchedule.objects.filter(
            course_schedule__course__school=school,
        )
