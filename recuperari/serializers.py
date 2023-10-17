from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import (Course, CourseDescription, CourseSchedule, MakeUp, School,
                     Session, SessionsDescription, Student, Trainer,
                     TrainerSchedule, User)
from .services.trainer import TrainerService

class CourseDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDescription
        fields = ['short_description', 'long_description']


class CourseSerializer(serializers.ModelSerializer):
    course_description = serializers.SerializerMethodField(read_only=True,)
    next_possible_course = serializers.StringRelatedField(
        many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['course_type', 'course_description', 'next_possible_course']

    def get_course_description(self, obj):
        # Serialize the course_description field manually
        course_descriptions = obj.course_description
        return CourseDescriptionSerializer(course_descriptions, many=True).data


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = ['students']


class SessionDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionsDescription
        fields = ['course', 'min_session_no_description',
                  'max_session_no_description']


class SessionSerializer(serializers.ModelSerializer):
    course_session = CourseScheduleSerializer()

    class Meta:
        model = Session
        fields = ['course_session', 'session_passed', 'date',
                  'session_no', 'absent_participants', 'made_up', 'course_session']


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


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = '__all__'


class SignInSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    token = serializers.HiddenField(default=None)

    class Meta:
        model = User
        fields = [
            "password",
            "token",
            "username",
        ]

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        username = attrs.get("username", None)
        password = attrs.get("password", None)

        if username is None:
            raise serializers.ValidationError(
                "A username is required to sign-in.")

        if password is None:
            raise serializers.ValidationError(
                "A password is required to sign-in.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                "This combination of username and password is invalid."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user has been deactivated.")

        return data


class SchoolSetupSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(read_only=True)

    class Meta:
        model = School
        fields = [
            "name",
            "phone_contact",
            "email_contact",
            "room_count",
            "owner_name",
        ]


class StudentCreateUpdateSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "school",
            "participant_name",
            "participant_parent_name",
            "parent_phone_number",
            "parent_email",
        ]


class TrainerCreateUpdateSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta:
        model = Trainer
        fields = [
            "id",
            "name",
            "phone_contact",
            "email_contact",
        ]

    def create(self, validated_data):
        validated_data["user"] = TrainerService.create_user_for_trainer(
            username=self.validated_data["name"].replace(" ", ".").lower(),
        )
        return super().create(validated_data)
