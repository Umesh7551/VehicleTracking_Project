# Generated by Django 5.0.1 on 2024-03-14 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPSTracking_App', '0002_alter_car_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker_data',
            name='status',
            field=models.CharField(default='01', max_length=2),
        ),
    ]
