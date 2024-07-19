from django.contrib.auth.models import User
from django.db import models


class BlackListTokenAccess(models.Model):
    token = models.TextField()
    user_id = models.ForeignKey(
        User,                  # Model (Table) to set foreign key relation
        null=False,                  # Allow null values in this field
        blank=False,                 # Allow blank values in this field
        on_delete=models.CASCADE    # If a User is deleted, all related inactive tokens too
    )
    added_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class ParkingLot(models.Model):
    name = models.TextField(max_length=30, null=False, blank=False)
    created_at = models.DateField(auto_now_add=True, blank=False)
    max_num_vehicles = models.IntegerField(null=False, blank=False)
    num_vehicles = models.IntegerField(default=0)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)


class User_ParkingLots(models.Model):
    user_id = models.ForeignKey(
        User,                       # Model (Table) to set foreign key relation
        null=False,                 # Dont allow null values in this field
        blank=False,                # Dont allow blank values in this field
        on_delete=models.CASCADE    # If a User is deleted, all related Parking association too
    )
    parking_id = models.ForeignKey(
        ParkingLot,                 # Model (Table) to set foreign key relation
        null=False,                 # Dont allow null values in this field
        blank=False,                # Dont allow blank values in this field
        on_delete=models.CASCADE    # If a Parking is deleted, all related User association too
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

class VehicleParkingRegister(models.Model):
    vehicle_plate = models.TextField(max_length=6, null=False, blank=False)
    parking_id = models.ForeignKey(
        ParkingLot,                 # Model (Table) to set foreign key relation
        null=False,                 # Dont allow null values in this field
        blank=False,                # Dont allow blank values in this field
        on_delete=models.DO_NOTHING # If a User is deleted, all related inactive tokens too
    )
    entry_time = models.DateTimeField(auto_now_add=True)
    parking_spot = models.IntegerField(null=False, blank=False)
    remarks = models.TextField(max_length=300, null=True, blank=True)

class VehicleParkingHistorical(ParkingLot):
    exit_time = models.DateTimeField(auto_now_add=True)
    hours = models.SmallIntegerField(null=False, blank=False)
    income = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    class Meta:
        # This specifies that the model should use the table of the derived class
        # instead of the base class's table
        verbose_name = "VehicleParkingHistorical"
        verbose_name_plural = "VehicleParkingHistorical"

class ParkingDailyIncomes(models.Model):
    parking_id = models.ForeignKey(
        ParkingLot,                 # Model (Table) to set foreign key relation
        null=False,                 # Dont allow null values in this field
        blank=False,                # Dont allow blank values in this field
        on_delete=models.DO_NOTHING # If a User is deleted, all related inactive tokens too
    )
    date = models.DateField(null=False, blank=False)
    num_inputs = models.BigIntegerField(default=0)
    incomes = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
