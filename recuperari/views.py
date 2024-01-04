from itertools import chain

from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from lsc_recuperari import settings

from .authentication import CookieJWTAuthentication
from .models import Course, CourseSchedule, DaysOff, Room, School, Student, Trainer, User, TrainerFromSchool, Session
from .permissions import IsCoordinator, IsStudent, IsTrainer
from .serializers import (
    AbsencesSerializer,
    CourseScheduleSerializer,
    CourseSerializer,
    DaysOffSerializer,
    ImportSerializer,
    MakeUpSerializer,
    ResetPasswordSerializer,
    RoomSerializer,
    SessionDescriptionSerializer,
    SessionListSerializer,
    SessionSerializer,
    StudentCreateUpdateSerializer,
    StudentsEmailSerializer,
    SchoolSetupSerializer,
    SignInSerializer,
    TrainerFromSchoolSerializer,
    TrainerCreateUpdateSerializer,
    TrainerScheduleSerializer,
    StudentCourseScheduleSerializer
)
from .services.absence import AbsenceService
from .services.course import CourseService
from .services.emails import EmailService
from .services.makeup import MakeUpService
from .services.session import SessionService
from .services.students import StudentService
from .services.trainer import TrainerService
from .services.users import UserService
from .utils import (check_excel_format_in_request_data,
                    format_whised_make_up_times,)


class CoursesList(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        school = self.request.user.course_school.first()
        return school.school_courses.all()


class CourseScheduleList(generics.ListAPIView):
    serializer_class = CourseScheduleSerializer

    def get_queryset(self):
        school = self.request.user.user_school.first()
        return CourseSchedule.objects.filter(school=school)


class CourseScheduleMatchingList(generics.ListAPIView):
    serializer_class = CourseScheduleSerializer

    def get_queryset(self):
        current_schedule_id = self.kwargs['pk']
        user_school = self.request.user.user_school.all().first()
        current_schedule = CourseSchedule.objects.get(id=current_schedule_id)
        # Scenario 1: Same day, same time, same course
        scenario_1 = CourseSchedule.objects.filter(
            day=current_schedule.day,
            time=current_schedule.time,
            course=current_schedule.course,
        ).exclude(id=current_schedule_id).exclude(school=user_school)
        # Scenario 2: Same day, different time, same course
        scenario_2 = CourseSchedule.objects.filter(
            day=current_schedule.day,
            course=current_schedule.course,
        ).exclude(id=current_schedule_id).exclude(time=current_schedule.time).exclude(school=user_school)
        # Scenario 3: Different day, different time, same course
        scenario_3 = CourseSchedule.objects.filter(
            course=current_schedule.course,
        ).exclude(id=current_schedule_id).exclude(day=current_schedule.day).exclude(school=user_school)
        # Combine scenarios and remove duplicates
        combined_schedules = (scenario_1 | scenario_2 | scenario_3).distinct()
        return combined_schedules


class SessionCourseList(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_session_by_course_schedule_id(self.kwargs['pk'])


class SessionInfoList(generics.RetrieveAPIView, generics.GenericAPIView):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

    def retrieve(self, request, *args, **kwargs):
        session = SessionService.get_session_by_id(self.kwargs['pk']).first()
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SessionDescriptionList(generics.ListAPIView):
    serializer_class = SessionDescriptionSerializer

    def get_queryset(self):
        return SessionService.get_session_description_by_course_id(self.kwargs['course_id'])


class SessionsListView(generics.ListAPIView):
    serializer_class = SessionListSerializer
    permission_classes = [IsAuthenticated, IsCoordinator or IsTrainer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def get_queryset(self):
        return SessionService.get_sessions_by_user_school(
            self.request.user)


class AbsencesListView(generics.ListAPIView):
    serializer_class = AbsencesSerializer
    permission_classes = [IsAuthenticated, IsCoordinator | IsTrainer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'absent_on_session',
        'absent_participant',
        'choosed_course_session_for_absence__date',
        'choosed_make_up_session_for_absence__datetime__date']

    def get_queryset(self):
        return AbsenceService.get_all_absences_from_school(
            self.request.user.course_school.first())


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
        absence_id = request.GET.get('absence_id')
        school = request.user.user_school.first()

        absence = AbsenceService.get_absence_by_id(absence_id)
        make_ups_for_session_in_current_school = MakeUpService.get_make_ups_for_session(
            absence, school)
        courses_for_session = SessionService.get_next_sessions_for_absence(
            absence, school)
        make_up_options = {
            "make_ups": make_ups_for_session_in_current_school,
            "courses": courses_for_session,
        }
        return Response(make_up_options, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class MakeUpChooseView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        session = None
        make_up = None
        absence = AbsenceService.get_absence_by_id(self.kwargs['absence_id'])
        if self.kwargs.get("session_option") and self.kwargs.get("session_option") != "None":
            session = SessionService.get_session_by_id(self.kwargs.get("session_option")).first()
            print(session)
            absence.choosed_course_session_for_absence = session
        elif self.kwargs.get("make_up_opton") and self.kwargs.get("make_up_opton") != "None":
            make_up = MakeUpService.get_make_up_by_id(self.kwargs.get("make_up_option")) 
            absence.choosed_make_up_session_for_absence = make_up
        absence.has_make_up_scheduled = True
        absence.save()
        # TODO: IMPLEMENT SEND MAIL FOR MAKE UP CONFIRMATION
        return Response({"message": "Absence updated"}, status=status.HTTP_200_OK)


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


class TrainerFromSchoolListView(generics.ListAPIView):
    serializer_class = TrainerFromSchoolSerializer

    def get_queryset(self):
        # Get the school from the authenticated user
        school = self.request.user.user_school.all().first()
        # Query the trainers from the school
        queryset = TrainerFromSchool.objects.filter(school=school)
        return queryset


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
        print(serializer.validated_data["send_mail"])
        print(serializer.validated_data["send_whatsapp"])
        if serializer.validated_data["send_mail"]:
            StudentService.send_emails_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                subject=serializer.validated_data["subject"],
                message=serializer.validated_data["message"],
            )
        if serializer.validated_data["send_whatsapp"]:
            StudentService.send_whatsapp_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                message=serializer.validated_data["message"],
            )
        return Response({"message": "Mails sent successfully"}, status.HTTP_200_OK)


class UploadCourseExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
        try:
            total_courses = CourseService.create_course_and_course_schedule_from_excel_by_school(
                request.data['file'], school)
            return Response({'message': f'Total cursuri create: {total_courses}'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadStudentsExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
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


class CourseScheduleDetailView(generics.ListAPIView, generics.GenericAPIView):
    serializer_class = CourseScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']

    def get_queryset(self):
        school = self.request.user.user_school.first()
        return CourseSchedule.objects.filter(school=school)


class SignInView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignInSerializer

    def post(self, request: Request):
        print(request.data)
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


class CheckUserRedirectView(APIView):
    def get(self, request):
        redirect_url = ""
        if request.user.role == "coordinator" and not request.user.user_school.all().exists():
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/school_create.html"
        elif request.user.role == "parent":
            # TODO: implement
            pass
        else:
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/today_sessions.html"
        return Response({"redirect_to": redirect_url}, status=status.HTTP_200_OK)


class DaysOffListView(generics.ListCreateAPIView):
    serializer_class = DaysOffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = DaysOff.objects.filter(school=school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


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


class TrainerFromSchoolListView(generics.ListAPIView):
    serializer_class = TrainerFromSchoolSerializer

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = TrainerFromSchool.objects.filter(school=school)
        return queryset


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


class StudentFirstDayListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsCoordinator)
    serializer_class = StudentCourseScheduleSerializer

    def get_queryset(self):
        return StudentService.get_students_first_day_of_course_by_school(
            school=self.request.user.course_school.first()
        )


class StudentAbsentView(APIView):
    def post(self, request, *args, **kwargs):
        student = StudentService.get_student_by_id(kwargs['student_id'])
        session = SessionService.get_session_by_id(kwargs["session_id"]).first()
        absence, created = AbsenceService.create_absent_student_for_session(
            student=student,
            session=session,)
        if created:
            MakeUpService.create_empty_make_up_session_for_absence(student, absence)
        return Response({"Student marked successfully as absent"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        absences = AbsenceService.get_all_absences_from_school(
            school=request.user.user_school.first())
        serializer = AbsencesSerializer(absences, many=True)
        return Response(serializer.data)


class SchoolCreateView(generics.CreateAPIView):
    serializer_class = SchoolSetupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = Room.objects.filter(school=school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())
