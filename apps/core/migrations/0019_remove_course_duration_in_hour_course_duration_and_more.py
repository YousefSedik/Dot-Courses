# Generated by Django 5.0.3 on 2024-03-26 03:14

from django.db import migrations, models

from datetime import timedelta
class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_test_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='duration_in_hour',
        ),
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.DurationField(default=timedelta),
        ),
        migrations.AddField(
            model_name='test',
            name='duration',
            field=models.DurationField(default=timedelta),
        ),
    ]