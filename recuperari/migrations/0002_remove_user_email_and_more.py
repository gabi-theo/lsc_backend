# Generated by Django 4.2.5 on 2023-10-15 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recuperari', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_reset_password_email_token_expired',
        ),
    ]
