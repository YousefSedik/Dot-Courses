# Generated by Django 5.0.3 on 2024-03-20 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_video_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='enrolled_counter',
            field=models.IntegerField(default=0),
        ),
    ]
