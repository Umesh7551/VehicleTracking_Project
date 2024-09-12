from django.contrib import admin
from .models import Car, GPSTracker, Tracker_data, Driver, RFID, Zone, Profile, FleetOwnerSupport


# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'address1', 'address2', 'city', 'state', 'country', 'mobile', 'user_id', 'fleetowner']
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


@admin.register(FleetOwnerSupport)
class FleetOwnerSupportAdmin(admin.ModelAdmin):
    list_display = ['id', 'fleetowner', 'fleetowner_support_user']