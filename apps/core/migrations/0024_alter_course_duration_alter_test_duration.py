# Generated by Django 5.0.3 on 2024-03-26 15:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_course_duration_alter_test_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(days=1)),
        ),
        migrations.AlterField(
            model_name='test',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(days=1)),
        ),
    ]