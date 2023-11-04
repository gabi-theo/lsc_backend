from django.contrib import admin

from .models import (Course, CourseDays, CourseDescription, CourseSchedule,
                     MakeUp, School, Session, SessionsDescription, Student,
<<<<<<< HEAD
                     StudentCourseSchedule, TimeOff, Trainer, TrainerSchedule,
                     User)
=======
                     StudentCourseSchedule, Trainer, TrainerSchedule, User,
                     TimeOff, StudentMakeUp)
>>>>>>> 2ea569c5b2b5463ff52da90ad2ba9d1b4202075b

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
admin.site.register(User)
admin.site.register(StudentCourseSchedule)
admin.site.register(TimeOff)
admin.site.register(StudentMakeUp)
