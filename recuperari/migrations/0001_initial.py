# Generated by Django 4.2.5 on 2023-10-30 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_reset_password_email_token_expired', models.BooleanField(default=True)),
                ('is_reset_password_token_expired', models.BooleanField(default=True)),
                ('role', models.CharField(blank=True, choices=[('trainer', 'Trainer'), ('student', 'Student'), ('coordinator', 'Coordinator')], max_length=20, null=True)),
                ('is_reset_password_needed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('course_type', models.CharField(max_length=50)),
                ('next_possible_course', models.ManyToManyField(blank=True, related_name='next_course', to='recuperari.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('luni', 'Luni'), ('marti', 'Marti'), ('miercuri', 'Miercuri'), ('joi', 'Joi'), ('vineri', 'Vineri'), ('sambata', 'Sambata'), ('duminica', 'Duminica')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CourseSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=50)),
                ('total_sessions', models.SmallIntegerField()),
                ('first_day_of_session', models.DateField()),
                ('last_day_of_session', models.DateField()),
                ('day', models.CharField(choices=[('luni', 'Luni'), ('marti', 'Marti'), ('miercuri', 'Miercuri'), ('joi', 'Joi'), ('vineri', 'Vineri'), ('sambata', 'Sambata'), ('duminica', 'Duminica')], max_length=15)),
                ('time', models.TimeField()),
                ('course_type', models.CharField(choices=[('onl', 'Online'), ('hbr', 'Hibrid'), ('sed', 'Sediu')], max_length=10)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_schedules', to='recuperari.course')),
            ],
        ),
        migrations.CreateModel(
            name='MakeUp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('make_up_on', models.DateTimeField()),
                ('type', models.CharField(choices=[('onl', 'Online cu alta grupa'), ('online_make_up', 'Recuperare online'), ('sed', 'La sediu cu alta grupa'), ('hbr', 'Hibrid cu alta grupa'), ('on_stie_make_up', 'Recuperare la sediu')], max_length=50)),
                ('duration_in_minutes', models.SmallIntegerField(default=30)),
                ('make_up_approved', models.BooleanField(default=False)),
                ('make_up_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('phone_contact', models.CharField(max_length=15)),
                ('email_contact', models.EmailField(max_length=254)),
                ('room_count', models.PositiveSmallIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_school', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('participant_name', models.CharField(max_length=50)),
                ('participant_parent_name', models.CharField(max_length=50)),
                ('parent_phone_number', models.CharField(max_length=20)),
                ('parent_email', models.CharField(max_length=50)),
                ('student_active', models.BooleanField(default=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_students', to='recuperari.school')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeOff',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_day', models.DateField()),
                ('end_day', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('phone_contact', models.CharField(max_length=15)),
                ('email_contact', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrainerSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('available_from', models.DateField()),
                ('available_to', models.DateField()),
                ('available_hour_from', models.TimeField()),
                ('available_hour_to', models.TimeField()),
                ('available_for_make_up', models.BooleanField(default=True)),
                ('available_for_course', models.BooleanField(default=True)),
                ('online_only', models.BooleanField(default=False)),
                ('available_days', models.ManyToManyField(to='recuperari.coursedays')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.school')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.trainer')),
            ],
        ),
        migrations.CreateModel(
            name='StudentMakeUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('made_up', models.BooleanField(default=False)),
                ('make_up_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_make_ups', to='recuperari.makeup')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_make_ups', to='recuperari.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourseSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('course_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.courseschedule')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.student')),
            ],
            options={
                'unique_together': {('course_schedule', 'student')},
            },
        ),
        migrations.CreateModel(
            name='SessionsDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('min_session_no_description', models.IntegerField()),
                ('max_session_no_description', models.IntegerField()),
                ('description', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_descriptions', to='recuperari.course')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_passed', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('session_no', models.SmallIntegerField()),
                ('can_have_online_make_up', models.BooleanField(default=True)),
                ('can_have_on_site_make_up', models.BooleanField(default=True)),
                ('absent_participants', models.ManyToManyField(to='recuperari.student')),
                ('course_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.courseschedule')),
                ('session_trainer', models.ForeignKey(blank=True, help_text='In case other trainer will replace a trainer', null=True, on_delete=django.db.models.deletion.SET_NULL, to='recuperari.trainer')),
            ],
        ),
        migrations.AddField(
            model_name='makeup',
            name='make_up_for_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.session'),
        ),
        migrations.AddField(
            model_name='makeup',
            name='make_up_trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recuperari.trainer'),
        ),
        migrations.AddField(
            model_name='makeup',
            name='students',
            field=models.ManyToManyField(through='recuperari.StudentMakeUp', to='recuperari.student'),
        ),
        migrations.AddField(
            model_name='courseschedule',
            name='default_trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recuperari.trainer'),
        ),
        migrations.AddField(
            model_name='courseschedule',
            name='students',
            field=models.ManyToManyField(related_name='course_schedule_students', through='recuperari.StudentCourseSchedule', to='recuperari.student'),
        ),
        migrations.CreateModel(
            name='CourseDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('short_description', models.TextField(max_length=100)),
                ('long_description', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_description', to='recuperari.course')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_courses', to='recuperari.school'),
        ),
    ]
