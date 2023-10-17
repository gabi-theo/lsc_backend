from django.db.models import Q

from recuperari.models import Trainer, TrainerSchedule, User
from recuperari.utils import random_password_generator
from recuperari.services.emails import EmailService


class TrainerService:
    @staticmethod
    def get_trainer_session_by_trainer_id(trainer_id):
        return TrainerSchedule.objects.filter(trainer__id=trainer_id)

    @staticmethod
    def get_trainers_available_in_school_for_given_interval(
        wished_make_up_date,
        wished_make_up_max_time,
        wished_make_up_min_time,
        school,
    ):
        return TrainerSchedule.objects.filter(
            Q(available_from__lte=wished_make_up_date, available_to__gte=wished_make_up_date) &
            Q(available_hour_from__lte=wished_make_up_max_time, available_hour_to__gte=wished_make_up_min_time) &
            Q(available_for_make_up=True) &
            Q(school=school)
        )

    @staticmethod
    def get_trainer_by_id(trainer_id):
        return Trainer.objects.filter(id=trainer_id).first()

    @staticmethod
    def create_user_for_trainer_and_send_emai(username, trainer_email):
        password = random_password_generator()
        user = User.objects.create_user(
            username=username,
            password=password,
            is_reset_password_needed=True,
            role="trainer",
        )
        print(password)
        send_to = [trainer_email]
        EmailService.send_email(
            recipient_emails=send_to,
            message="test email",
            subject="test subject",
            sender="gabi.isaila@logiscool.com"
        )
        return user
