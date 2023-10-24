import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    User model manager where username is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_("The username must be set"))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("trainer", "Trainer"),
        ("student", "Student"),
        ("coordinator", "Coordinator"),
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50, unique=True)
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_reset_password_email_token_expired = models.BooleanField(default=True)
    is_reset_password_token_expired = models.BooleanField(default=True)
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES, blank=True, null=True)
    is_reset_password_needed = models.BooleanField(default=False)
    objects = UserManager()



    def _str_(self):
        return self.get_username()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


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
    room_count = models.PositiveSmallIntegerField(
        null=False,
        blank=False
    )

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
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, unique=True)
    phone_contact = models.CharField(max_length=15)
    email_contact = models.EmailField()


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_students",
    )
    participant_name = models.CharField(max_length=50, null=False, blank=False)
    participant_parent_name = models.CharField(
        max_length=50, null=False, blank=False)
    parent_phone_number = models.CharField(
        max_length=20, null=False, blank=False)
    parent_email = models.CharField(max_length=50, null=False, blank=False)
    student_active = models.BooleanField(default=True)

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
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='course_schedules')
    group_name = models.CharField(max_length=50, null=False, blank=False)
    total_sessions = models.SmallIntegerField()
    first_day_of_session = models.DateField(null=False, blank=False)
    last_day_of_session = models.DateField(null=False, blank=False)
    day = models.CharField(
        max_length=15,
        choices=DAYS,
    )
    time = models.TimeField(null=False)
    default_trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(
        Student,
        related_name="course_schedule_students",
        through='StudentCourseSchedule',
    )
    course_type = models.CharField(max_length=10, choices=TYPE)

    def __str__(self) -> str:
        return self.group_name


class StudentCourseSchedule(models.Model):
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('course_schedule', 'student')

    def __str__(self) -> str:
        return self.student.participant_name + " " + self.course_schedule.group_name


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
    session_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="In case other trainer will replace a trainer",
    )
    session_passed = models.BooleanField(default=False)
    date = models.DateField()
    session_no = models.SmallIntegerField()
    absent_participants = models.ManyToManyField(Student)
    can_have_online_make_up = models.BooleanField(default=True)
    can_have_on_site_make_up = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.course_session} - {self.session_no}"


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
    make_up_trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    make_up_approved = models.BooleanField(default=False)
    make_up_completed = models.BooleanField(default=False)
    students = models.ManyToManyField(Student, through="StudentMakeUp")


class StudentMakeUp(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_make_ups")
    make_up_session = models.ForeignKey(MakeUp, on_delete=models.CASCADE, related_name="session_make_ups")
    made_up = models.BooleanField(default=False)


class CourseDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_description")
    short_description = models.TextField(max_length=100)
    long_description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


class SessionsDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="session_descriptions")
    min_session_no_description = models.IntegerField(null=False, blank=False)
    max_session_no_description = models.IntegerField(null=False, blank=False)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
