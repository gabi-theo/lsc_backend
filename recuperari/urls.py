from django.urls import path

from recuperari.views import (CourseScheduleDetailView, CoursesList,
                              MakeUpRequestNewView,
                              MakeUpSessionsAvailableView,
                              ResetPasswordView, SchoolSetupView,
                              SessionDescriptionList, SessionList, SignInView,
                              StudentProfileView, TrainerProfileView,
                              TrainerScheduleView, UploadCourseExcelView,
                              UploadStudentsExcelView, StudentCreateView,
                              TrainerCreateView, SignOutView)

urlpatterns = [
    path('courses/', CoursesList.as_view(), name='courses-list'),
    path(
        'sessions/<uuid:course_schedule_id>/',
        SessionList.as_view(),
        name='session_list'
    ),
    path(
        'session/description/<uuid:course_id>/',
        SessionDescriptionList.as_view(),
        name='session_description_list',
    ),
    path(
        'trainer_schedule/<uuid:pk>/',
        TrainerScheduleView.as_view(),
        name='trainer_schedule',
    ),
    path(
        "get_available_make_ups/",
        MakeUpSessionsAvailableView.as_view(),
        name="get_make_ups_for_session",
    ),
    path(
        "request_make_up/",
        MakeUpRequestNewView.as_view(),
        name="request_make_up",
    ),
    path(
        "course_excel_upload/",
        UploadCourseExcelView.as_view(),
        name="course_excel_upload"
    ),
    path(
        "students_excel_upload/",
        UploadStudentsExcelView.as_view(),
        name="students_excel_upload"
    ),
    path(
        "course_schedule_details/",
        CourseScheduleDetailView.as_view(),
    ),
    path(
        "auth/login/",
        SignInView.as_view(),
        name="login",
    ),
    path(
        "auth/logout/",
        SignOutView.as_view(),
    ),
    path(
        "auth/reset_password/",
        ResetPasswordView.as_view(),
        name="reset_password",
    ),
    path(
        "school-setup/",
        SchoolSetupView.as_view(),
        name="school-setup"
    ),
    path(
        "trainer-profile/<uuid:pk>",
        TrainerProfileView.as_view(),
        name="trainer-profile"
    ),
    path(
        "trainer-create",
        TrainerCreateView.as_view(),
        name="trainer-profile"
    ),
    path(
        "student-profile/<uuid:pk>",
        StudentProfileView.as_view(),
        name="student-profile"
    ),
    path(
        "student-create",
        StudentCreateView.as_view(),
        name="student-profile"
    ),
]
