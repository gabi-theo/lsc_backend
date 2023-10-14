from django.urls import path
from recuperari.views import (
    CoursesList,
    CourseScheduleDetailView,
    MakeUpRequestNewView,
    MakeUpSessionsAvailableView,
    SessionList,
    SessionDescriptionList,
    TrainerScheduleView,
    UploadCourseExcelView,
    UploadStudentsExcelView,
)

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
    )
]
    