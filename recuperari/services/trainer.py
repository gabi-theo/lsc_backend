from recuperari.models import TrainerSchedule
from django.db.models import Q


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