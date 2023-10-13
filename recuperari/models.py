from django.db import models
from django.contrib.auth.models import User
import uuid


class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_school",
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=50,
    )
    phone_contact = models.CharField(max_length=15)
    email_contact = models.EmailField()

    def __str__(self) -> str:
        return self.name


class CourseDays(models.Model):
    DAYS = (
        ("luni", "Luni"),
        ("marti", "Marti"),
        ("miercuri", "Miercuri"),
        ("joi", "Joi"),
        ("vineri", "Vineri"),
        ("sambata", "Sambata"),
        ("duminica", "Duminica"),
    )
    day = models.CharField(max_length=20, choices=DAYS)


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_courses",
    )
    next_possible_course = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='next_course'
    )
    course_type = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return self.course_type + " " + self.school.name


class Trainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    phone_contact = models.CharField(max_length=15)
    email_contact = models.EmailField()


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_students",
    )
    participant_name = models.CharField(max_length=50, null=False, blank=False)
    participant_parent_name = models.CharField(max_length=50, null=False, blank=False)
    parent_phone_number = models.CharField(max_length=20, null=False, blank=False)
    parent_email = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return self.participant_name


class CourseSchedule(models.Model):
    DAYS = (
        ("luni", "Luni"),
        ("marti", "Marti"),
        ("miercuri", "Miercuri"),
        ("joi", "Joi"),
        ("vineri", "Vineri"),
        ("sambata", "Sambata"),
        ("duminica", "Duminica"),
    )

    TYPE = (
        ("onl", "Online"),
        ("hbr", "Hibrid"),
        ("sed", "Sediu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_schedules')
    group_name = models.CharField(max_length=50, null=False, blank=False)
    total_sessions = models.SmallIntegerField()
    first_day_of_session = models.DateField(null=False, blank=False)
    last_day_of_session = models.DateField(null=False, blank=False)
    day = models.CharField(
        max_length=15,
        choices=DAYS,
    )
    time = models.TimeField(null=False)
    trainer = models.ManyToManyField(Trainer)
    students = models.ManyToManyField(Student)
    course_type = models.CharField(max_length=10, choices=TYPE)

    def __str__(self) -> str:
        return self.group_name


class TrainerSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    available_from = models.DateField()
    available_to = models.DateField()
    available_days = models.ManyToManyField(CourseDays)
    available_hour_from = models.TimeField()
    available_hour_to = models.TimeField()
    available_for_make_up = models.BooleanField(default=True)
    available_for_course = models.BooleanField(default=True)
    online_only = models.BooleanField(default=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE)


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_session = models.ForeignKey(
        CourseSchedule,
        on_delete=models.CASCADE,
    )
    session_passed = models.BooleanField(default=False)
    date = models.DateField()
    session_no = models.SmallIntegerField()
    absent_participants = models.ManyToManyField(Student)
    made_up = models.BooleanField(default=False)
    can_have_online_make_up = models.BooleanField(default=True)
    can_have_on_site_make_up = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.course_session} - {self.session_no}"


# TODO: Check if needed
# class StudentMakeUp(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE)
#     made_up = models.BooleanField(default=False)



class MakeUp(models.Model):
    MAKE_UP_SESSION_TYPE = (
        ("onl", "Online cu alta grupa"),
        ("online_make_up", "Recuperare online"),
        ("sed", "La sediu cu alta grupa"),
        ("hbr", "Hibrid cu alta grupa"),
        ("on_stie_make_up", "Recuperare la sediu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    make_up_for_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    make_up_on = models.DateTimeField()
    type = models.CharField(max_length=50, choices=MAKE_UP_SESSION_TYPE)
    duration_in_minutes = models.SmallIntegerField(default=30)
    make_up_trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    make_up_approved = models.BooleanField(default=False)
    make_up_completed = models.BooleanField(default=False)


class CourseDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_description")
    short_description = models.TextField(max_length=100)
    long_description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


class SessionsDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="session_descriptions")
    min_session_no_description = models.IntegerField(null=False, blank=False)
    max_session_no_description = models.IntegerField(null=False, blank=False)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
