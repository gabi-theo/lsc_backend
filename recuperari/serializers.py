from rest_framework import serializers
from .models import (
    Course,
    CourseDescription,
    MakeUp,
    Session,
    SessionsDescription,
    TrainerSchedule,
)


class CourseDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDescription
        fields = ['short_description', 'long_description']


class CourseSerializer(serializers.ModelSerializer):
    course_description = serializers.SerializerMethodField(read_only=True,)
    next_possible_course = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['course_type', 'course_description', 'next_possible_course']

    def get_course_description(self, obj):
        # Serialize the course_description field manually
        course_descriptions = obj.course_description
        return CourseDescriptionSerializer(course_descriptions, many=True).data


class SessionDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionsDescription
        fields = ['course', 'min_session_no_description', 'max_session_no_description', 'description']


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['course_session', 'session_passed', 'date', 'session_no', 'absent_participants', 'made_up']


class TrainerScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerSchedule
        fields = '__all__'


class MakeUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeUp
        fields = '__all__'


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()
