from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (Course, CourseDescription, CourseSchedule, MakeUp, School,
                     Session, SessionsDescription, Student, Trainer,
                     TrainerSchedule, User)
from .services.trainer import TrainerService
from .services.students import StudentService


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
                  'max_session_no_description', 'description', 'created_at', 'updated_at']


class SessionSerializer(serializers.ModelSerializer):
    course_session = CourseScheduleSerializer()

    class Meta:
        model = Session
        fields = ['id', 'course_session', 'session_passed', 'date',
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
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "username",
            "password",
            "participant_name",
            "participant_parent_name",
            "parent_phone_number",
            "parent_email",
        ]

    def validate(self, attrs):
        attrs["user"] = StudentService.create_user_for_student(
            attrs["username"],
            attrs["password"],
        )
        del attrs["password"]
        del attrs["username"]
        return super().validate(attrs)

    def create(self, validated_data):
        request_user = self.context["request"].user
        print(validated_data)
        validated_data["school"] = request_user.course_school.first()
        return super().create(validated_data)


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
        validated_data["user"] = TrainerService.create_user_for_trainer_and_send_emai(
            username=self.validated_data["name"].replace(" ", ".").lower(),
            trainer_email=self.validated_data["email_contact"]
        )
        return super().create(validated_data)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    user = serializers.HiddenField(default=None)

    class Meta:
        fields = [
            "password",
            "user",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        request = self.context["request"]

        user = request.user
        validate_password(attrs["password"])

        attrs["user"] = user

        return attrs


class StudentsEmailSerializer(serializers.Serializer):
    groups = serializers.CharField()
    subject = serializers.CharField()
    message = serializers.CharField()
    send_mail = serializers.BooleanField(default=True)
    send_whatsapp = serializers.BooleanField(default=False)

    class Meta:
        fields = [
            "groups",
            "subject",
            "message",
            "send_mail",
            "send_whatsapp",
        ]
