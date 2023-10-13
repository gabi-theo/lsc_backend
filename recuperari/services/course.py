import pandas as pd
from recuperari.models import Course, CourseSchedule
from recuperari.utils import map_to_bool


class CourseService:
    @staticmethod
    def get_course_schedule_by_group_name_day_and_time(
        group_name,
        day,
        time,
    ):  
        try:
            CourseSchedule.objects.get(
                group_name=group_name,
                day=day,
                time=time)
        except Exception as e:
            print(f"Error for group_name{group_name} on day {day} and time {time}")
            pass
        return CourseSchedule.objects.filter(
            group_name=group_name,
            day=day,
            time=time
        ).first()

    @staticmethod
    def create_course_and_course_schedule_from_excel_by_school(
        excel_file,
        school,
    ):
        # Read the Excel file
        df = pd.read_excel(excel_file, skiprows=[0])
        # Loop through the rows and create CourseSchedule objects
        for _, row in df.iterrows():
            course, _ = Course.objects.get_or_create(school=school, course_type=row['courseType_name'])
            CourseSchedule.objects.create(
                course=course,
                group_name=row['name'],
                total_sessions=row['totalSessions'],
                first_day_of_session=row['firstDay'],
                last_day_of_session=row['lastDay'],
                day=row['schedule_times'].split(" ")[0],
                time=row['schedule_times'].split(" ")[1],
                course_type="onl" if map_to_bool(row["online"]) else "sed"
            )

    @classmethod
    def add_student_to_course_schedule_by_group_name_day_and_time(
        cls,
        student,
        group_name,
        day,
        time,
    ):
        course_schedule = cls.get_course_schedule_by_group_name_day_and_time(
            group_name, day, time,
        )
        course_schedule.students.add(student)
