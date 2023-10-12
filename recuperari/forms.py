from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import School, Course


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SchoolRegistrationForm(forms.ModelForm):
    class Meta:
        model = School
        exclude = ('user', 'id')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.instance.user = self.user


class TimeInput(forms.TimeInput):
    input_type = 'time'


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['school', 'id']
        widgets = {
            'time': TimeInput(),
        }
