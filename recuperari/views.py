from itertools import chain

from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CookieJWTAuthentication
from .models import Course, CourseSchedule, School, Student, Trainer, User
from .permissions import IsCoordinator, IsStudent, IsTrainer
from .serializers import (CourseScheduleSerializer, CourseSerializer,
                          ImportSerializer, MakeUpSerializer,
                          ResetPasswordSerializer,
                          SchoolSetupSerializer, SessionDescriptionSerializer,
                          SessionListSerializer,
                          SessionSerializer, SignInSerializer,
                          StudentCreateUpdateSerializer,
                          StudentsEmailSerializer,
                          TrainerCreateUpdateSerializer,
                          TrainerScheduleSerializer,
                          StudentCourseScheduleSerializer)
from .services.course import CourseService
from .services.emails import EmailService
from .services.makeup import MakeUpService
from .services.session import SessionService
from .services.students import StudentService
from .services.trainer import TrainerService
from .services.users import UserService
from .utils import (check_excel_format_in_request_data,
                    format_whised_make_up_times)
from lsc_recuperari import settings


class CoursesList(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        school = self.request.user.course_school.first()
        return school.school_courses.all()


class SessionList(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_session_by_course_schedule_id(self.kwargs['course_schedule_id'])


class SessionDescriptionList(generics.ListAPIView):
    serializer_class = SessionDescriptionSerializer

    def get_queryset(self):
        return SessionService.get_session_description_by_course_id(self.kwargs['course_id'])


class SessionsAndMakeUpsListView(generics.ListAPIView):
    # TODO: implement filters for dates. Default should be today
    serializer_class = SessionListSerializer
    permission_classes = [IsAuthenticated, IsCoordinator, IsTrainer]

    def get_queryset(self):
        return SessionService.get_sessions_by_user_school(self.request.user)


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
                "session_id": "ff867fe5-d7cc-4ce3-a6af-8c8fd43d3dbe"
            }
        """
        session_id = request.data.get('session_id')
        school = request.user.course_school.first()

        session = SessionService.get_session_by_id(session_id)
        make_ups_for_session_in_current_school = MakeUpService.get_make_ups_for_school_by_session(
            school, session)
        make_ups_for_session_in_other_schools = MakeUpService.get_make_ups_excluding_current_school_by_session(
            school, session)
        all_make_ups = list(
            chain(
                make_ups_for_session_in_current_school,
                make_ups_for_session_in_other_schools,
            )
        )
        if len(all_make_ups) > 0:
            serializer = MakeUpSerializer(all_make_ups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'detail': 'MakeUps not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class TrainersScheduleAvailableView(generics.GenericAPIView):
    serializer_class = TrainerScheduleSerializer

    def get(self, request, *args, **kwargs):
        school_id = request.user.course_school.first().id
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
            serializer = TrainerScheduleSerializer(
                trainer_schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'MakeUps not found'}, status=status.HTTP_404_NOT_FOUND)


class MakeUpRequestNewView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = MakeUpSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SendEmailToGroupsView(generics.GenericAPIView):
    serializer_class = StudentsEmailSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["send_mail"]:
            StudentService.send_emails_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                subject=serializer.validated_data["subject"],
                message=serializer.validated_data["message"],
            )
        if serializer.validated_data["send_whatsapp"]:
            StudentService.send_whatsapp_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                subject=serializer.validated_data["subject"],
                message=serializer.validated_data["message"],
            )
        return Response({"message": "Mails sent successfully"}, status.HTTP_200_OK)


class UploadCourseExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = request.user.course_school.first()
        try:
            CourseService.create_course_and_course_schedule_from_excel_by_school(
                request.data['file'], school)
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadStudentsExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = request.user.course_school.first()
        try:
            StudentService.create_student_from_excel_and_assign_it_to_school_course(
                request.data['file'],
                school,
            )
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadStudentCourseScheduleFirstDayView(APIView):
    permission_classes = (IsAuthenticated, IsCoordinator)
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = request.user.course_school.first()
        try:
            StudentService.add_student_start_day_of_course(
                request.data['file'],
                school,
            )
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseScheduleDetailView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = CourseScheduleSerializer

    def get_queryset(self):
        school = self.request.user.course_school.first()
        return CourseSchedule.objects.filter(course__school=school)


class SignInView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignInSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.get_user_by_username(
            serializer.validated_data["username"])
        user.save()
        response = Response(self.get_serializer(user).data)
        CookieJWTAuthentication.login(user, response)
        return response


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(request):
        response = Response({"message": "Bye, see you soon 😌"})
        response.delete_cookie(settings.AUTH_COOKIE_KEY)

        return response


class SchoolSetupView(mixins.CreateModelMixin,
                      generics.GenericAPIView,
                      ):

    serializer_class = SchoolSetupSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class StudentProfileView(generics.RetrieveUpdateDestroyAPIView, generics.GenericAPIView):

    serializer_class = StudentCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def get_queryset(self):
        return StudentService.get_student_by_id(self.kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        student = get_object_or_404(Student, pk=self.kwargs["pk"])
        user = student.user
        user.delete()
        return Response("Student deleted", status=status.HTTP_204_NO_CONTENT)


class StudentCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = StudentCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TrainerProfileView(
    generics.RetrieveUpdateDestroyAPIView,
    generics.GenericAPIView
):

    serializer_class = TrainerCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def get_queryset(self):
        return TrainerService.get_trainer_by_id(self.kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        trainer = get_object_or_404(Trainer, pk=self.kwargs["pk"])
        user = trainer.user
        user.delete()
        return Response("Trainer deleted", status=status.HTTP_204_NO_CONTENT)


class TrainerCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = TrainerCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCoordinator | IsTrainer]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        response = Response({"message": "Password Reset Successfully"})
        user.set_password(serializer.validated_data.get("password"))
        user.is_reset_password_needed = False
        user.save()

        return response


class StudentCourseScheduleListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsCoordinator)
    serializer_class = StudentCourseScheduleSerializer

    def get_queryset(self):
        return StudentService.get_students_first_day_of_course_by_school(
            school=self.request.user.course_school.first()
        )
