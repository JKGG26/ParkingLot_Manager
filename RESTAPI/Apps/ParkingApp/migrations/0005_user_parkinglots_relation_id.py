# Generated by Django 5.0.7 on 2024-07-20 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ParkingApp', '0004_alter_parkinglot_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_parkinglots',
            name='relation_id',
            field=models.TextField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
