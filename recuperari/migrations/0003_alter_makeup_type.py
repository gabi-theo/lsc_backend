# Generated by Django 4.2.5 on 2023-10-27 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recuperari', '0002_alter_studentcourseschedule_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makeup',
            name='type',
            field=models.CharField(choices=[('onl', 'Online cu alta grupa'), ('online_make_up', 'Recuperare online'), ('sed', 'La sediu cu alta grupa'), ('hbr', 'Hibrid cu alta grupa'), ('on_site_make_up', 'Recuperare la sediu')], max_length=50),
        ),
    ]
