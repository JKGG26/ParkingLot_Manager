# Generated by Django 5.0.7 on 2024-07-19 22:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ParkingApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=30)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('max_num_vehicles', models.IntegerField()),
                ('num_vehicles', models.IntegerField(default=0)),
                ('price_per_hour', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleParkingHistorical',
            fields=[
                ('parkinglot_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ParkingApp.parkinglot')),
                ('exit_time', models.DateTimeField(auto_now_add=True)),
                ('hours', models.IntegerField(max_length=2)),
                ('income', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'verbose_name': 'VehicleParkingHistorical',
                'verbose_name_plural': 'VehicleParkingHistorical',
            },
            bases=('ParkingApp.parkinglot',),
        ),
        migrations.CreateModel(
            name='ParkingDailyIncomes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('num_inputs', models.IntegerField(default=0, max_length=8)),
                ('incomes', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('parking_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ParkingApp.parkinglot')),
            ],
        ),
        migrations.CreateModel(
            name='User_ParkingLots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parking_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ParkingApp.parkinglot')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleParkingRegister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_plate', models.TextField(max_length=6)),
                ('entry_time', models.DateTimeField(auto_now_add=True)),
                ('parking_spot', models.IntegerField()),
                ('remarks', models.TextField(blank=True, max_length=300, null=True)),
                ('parking_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ParkingApp.parkinglot')),
            ],
        ),
    ]
