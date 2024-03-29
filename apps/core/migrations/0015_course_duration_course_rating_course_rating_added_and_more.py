# Generated by Django 5.0.3 on 2024-03-25 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AddField(
            model_name='course',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=1),
        ),
        migrations.AddField(
            model_name='course',
            name='rating_added',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.CharField(max_length=1),
        ),
    ]
