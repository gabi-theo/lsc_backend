# Generated by Django 4.2.5 on 2023-12-12 18:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recuperari', '0003_remove_trainer_name_trainer_first_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainerFromSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='school_trainers', to='recuperari.school')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recuperari.trainer')),
            ],
        ),
    ]