# Generated by Django 4.2.5 on 2023-12-12 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recuperari', '0004_trainerfromschool'),
    ]

    operations = [
        migrations.CreateModel(
            name='DaysOff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_day_off', models.DateField()),
                ('last_day_off', models.DateField()),
                ('day_off_info', models.CharField(max_length=50)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.school')),
            ],
        ),
    ]