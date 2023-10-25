from datetime import datetime, timedelta
from math import ceil

from django.db.models.signals import post_save
from django.dispatch import receiver

from recuperari.models import CourseSchedule, Session, TimeOff


@receiver(post_save, sender=CourseSchedule)
def create_session(sender, instance, created, **kwargs):

    if created:
        # manually keep track of assigned sessions and the last assigned session since we might need to push some back
        first_day = instance.first_day_of_session
        sessions_assigned = 0
        last_session_date_tried = first_day

        # convert session day name to datetime weekday
        str_to_weekday = {
            "luni": 0,
            "marti": 1,
            "miercuri": 2,
            "joi": 3,
            "vineri": 4,
            "sambata": 5,
            "duminica": 6
        }

        # convert datetime weekday to session day name
        weekday_to_str = {
            0: "luni",
            1: "marti",
            2: "miercuri",
            3: "joi",
            4: "vineri",
            5: "sambata",
            6: "duminica"
        }

        # ensure we assign the session to the correct day
        if weekday_to_str[last_session_date_tried.weekday()] != instance.day:
            last_session_date_tried += timedelta(days=(str_to_weekday[instance.day] -
                                                       last_session_date_tried.weekday()) % 7)

        # do not assign more sessions than specified by the schedule
        while sessions_assigned < instance.total_sessions:

            # check that the session doesn't start when it's time off
            time_off = TimeOff.objects.filter(
                start_day__lt=last_session_date_tried, end_day__gt=last_session_date_tried)

            if not time_off:

                # don't assign sessions past the last day of the course schedule
                if last_session_date_tried > instance.last_day_of_session:
                    break   # very graceful handling

                # all good, create session
                sessions_assigned += 1
                Session.objects.create(
                    course_session=instance,
                    date=last_session_date_tried,
                    session_no=sessions_assigned,
                )

                # sessions should be a week apart
                last_session_date_tried += timedelta(weeks=1)
            else:

                # compute the first session weekday that comes after the last time_off day
                difference = time_off[0].end_day - last_session_date_tried
                last_session_date_tried += timedelta(
                    weeks=ceil(difference.days / 7))  # // might be faster idk
