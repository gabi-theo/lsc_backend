from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver

from recuperari.models import CourseSchedule, Session


@receiver(post_save, sender=CourseSchedule)
def create_session(sender, instance, created, **kwargs):
    if created:
        for session_no in range(1, instance.total_sessions + 1):
            session_date = instance.first_day_of_session + \
                timedelta(days=7 * (session_no - 1))
            Session.objects.create(
                course_session=instance,
                date=session_date,
                session_no=session_no,
            )
