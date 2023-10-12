from itertools import chain
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import (
    Course,
    School,
)
from .serializers import (
    CourseSerializer,
    ImportSerializer,
    MakeUpSerializer,
    SessionSerializer,
    SessionDescriptionSerializer,
    TrainerScheduleSerializer,
)
from .services.course import CourseService
from .services.makeup import MakeUpService
from .services.session import SessionService
from .services.trainer import TrainerService
from .utils import format_whised_make_up_times


class CoursesList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class SessionList(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_session_by_course_schedule_id(self.kwargs['course_schedule_id'])


class SessionDescriptionList(generics.ListAPIView):
    serializer_class = SessionDescriptionSerializer

    def get_queryset(self):
        return SessionService.get_session_description_by_course_id(self.kwargs['course_id'])


class TrainerScheduleView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    serializer_class = TrainerScheduleSerializer

    def get_queryset(self):
        return TrainerService.get_trainer_session_by_trainer_id(self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MakeUpSessionsAvailableView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = MakeUpSerializer

    def get(self, request, *args, **kwargs):
        # TODO: TEST ALL USE-CASES AND UPDATE FILTER CONDITIONS
        """
            view for getting all available make_ups for a session
            body_example:{
                "school_id": "2d3db5ad-b3da-46f8-9d4b-0e65fdbe2f30",
                "session_id": "ff867fe5-d7cc-4ce3-a6af-8c8fd43d3dbe"
            }
        """
        session_id = request.data.get('session_id')
        school = request.data.get("school_id")

        session = SessionService.get_session_by_id(session_id)
        make_ups_for_session_in_current_school = MakeUpService.get_make_ups_for_school_by_session(school, session)
        make_ups_for_session_in_other_schools = MakeUpService.get_make_ups_excluding_current_school_by_session(school, session)
        all_make_ups = list(
            chain(
                make_ups_for_session_in_current_school,
                make_ups_for_session_in_other_schools,
            )
        )
        if len(all_make_ups)>0:
            serializer = MakeUpSerializer(all_make_ups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'detail': 'MakeUps not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class TrainersScheduleAvailableView(generics.GenericAPIView):
    serializer_class = TrainerScheduleSerializer

    def get(self, request, *args, **kwargs):
        school_id = request.data.get("school_id")
        wished_make_up_date, wished_make_up_min_time, wished_make_up_max_time = format_whised_make_up_times(
            request.data.get("wished_make_up_date"),
            request.data.get("wished_make_up_min_time"),
            request.data.get("wished_make_up_max_time"),
        )

        # check all trainers from the school that are available in the given interval
        trainer_schedules = TrainerService.get_trainers_available_in_school_for_given_interval(
            wished_make_up_date,
            wished_make_up_max_time,
            wished_make_up_min_time,
            school_id,
        )
        if trainer_schedules.exists():
            serializer = TrainerScheduleSerializer(trainer_schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'MakeUps not found'}, status=status.HTTP_404_NOT_FOUND)


class MakeUpRequestNewView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = MakeUpSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SendMassEmail(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        pass


class UploadCourseExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({'error': 'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.data['file']
        if not excel_file.name.endswith('.xls') and not excel_file.name.endswith('.xlsx'):
            return Response(
                {'error': 'Invalid file format. Please provide an Excel file.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        school = School.objects.get(id="2d3db5ad-b3da-46f8-9d4b-0e65fdbe2f30")
        try:
            CourseService.create_course_and_course_schedule_from_excel_by_school(excel_file, school)
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)