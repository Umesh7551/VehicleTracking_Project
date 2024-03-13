from django.contrib import admin
from .models import FleetOwner, Car, GPSTracker, Tracker_data, Driver, RFID, Zone


# Register your models here.

@admin.register(FleetOwner)
class FleetOwnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'aadhar_number',
                    'pan_number', 'resident_proof']
    search_fields = ['email', 'contact_number', 'aadhar_number', 'pan_number']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'registration_number', 'registration_date', 'vehicle_name', 'colour', 'model',
                    'chassis_number', 'tracker', 'insurance', 'puc', 'seating_capacity', 'fuel_type',
                    'air_condition', 'owner']
    search_fields = ['registration_number', 'vehicle_name']


@admin.register(GPSTracker)
class GPSTrackerAdmin(admin.ModelAdmin):
    list_display = ['id', 'serial_number']
    search_fields = ['serial_number']


@admin.register(Tracker_data)
class Tracker_dataAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'zone', 'vendor', 'auth_key', 'latitude', 'longitude', 'speed', 'accuracy',
                    'timestamp', 'panic', 'ignition', 'air_condition']
    search_fields = ['vendor']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver_name', 'driver_licence_number', 'issue_date', 'valid_till', 'address',
                    'upload_licence', 'car', 'rfid']
    search_fields = ['driver_name', 'driver_licence_number']


@admin.register(RFID)
class RFIDAdmin(admin.ModelAdmin):
    list_display = ['id', 'rfid_code', 'driver']
    search_fields = ['rfid_code']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone_name']
    search_fields = ['zone_name']
