from django.contrib import admin
from .models import (
    Course,
    CourseDays,
    CourseDescription,
    CourseSchedule,
    MakeUp,
    School,
    Session,
    SessionsDescription,
    Student,
    Trainer,
    TrainerSchedule,
)

# Register your models here.
admin.site.register(School)
admin.site.register(Course)
admin.site.register(CourseDescription)
admin.site.register(Student)
admin.site.register(CourseSchedule)
admin.site.register(Trainer)
admin.site.register(TrainerSchedule)
admin.site.register(Session)
admin.site.register(SessionsDescription)
admin.site.register(CourseDays)
admin.site.register(MakeUp)
