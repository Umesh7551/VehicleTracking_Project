from django.contrib import admin
from .models import FleetOwner, Car, GPSTracker, Tracker_data, Driver, RFID


# Register your models here.

@admin.register(FleetOwner)
class FleetOwnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'password', 'confirm_password', 'contact_number', 'address', 'aadhar_number', 'pan_number', 'resident_proof']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'registration_number', 'registration_date', 'vehicle_name', 'colour', 'model', 'chassis_number', 'tracker_id', 'insurance', 'puc', 'seating_capacity', 'fuel_type', 'air_condition', 'owner']


@admin.register(GPSTracker)
class GPSTrackerAdmin(admin.ModelAdmin):
    list_display = ['id', 'serial_number']


@admin.register(Tracker_data)
class Tracker_dataAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'zone', 'vendor', 'auth_key', 'latitude', 'longitude', 'speed', 'accuracy', 'timestamp', 'panic', 'ignition', 'air_condition']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver_name', 'driver_licence_number', 'issue_date', 'valid_till', 'address', 'upload_licence', 'car', 'rfid']


@admin.register(RFID)
class RFIDAdmin(admin.ModelAdmin):
    list_display = ['id', 'rfid_code', 'driver']
