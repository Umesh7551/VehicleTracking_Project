import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fleetowner = models.ForeignKey(User, related_name='support_users', on_delete=models.CASCADE, null=True,
                                   blank=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin = models.CharField(max_length=6)
    country = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    profile_photo = models.ImageField(verbose_name='Profile Photo', upload_to='profile_photos/')

    class Meta:
        db_table = 'profile'

    def __str__(self):
        return f'{self.user} Profile'


class GPSTracker(models.Model):
    serial_number = models.CharField(verbose_name='Serial Number', max_length=200, unique=True)
    # car = models.OneToOneField(Car, on_delete=models.CASCADE)
    # fleet_owner = models.ForeignKey(FleetOwner, on_delete=models.CASCADE, blank=True, default='')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=1)  # Track who added the tracker
    class Meta:
        db_table = 'gpstracker'

    def __str__(self):
        return self.serial_number


class Car(models.Model):
    registration_number = models.CharField(verbose_name='Registration Number', max_length=20)
    registration_date = models.DateField(verbose_name='Registration Date')
    vehicle_name = models.CharField(verbose_name='Vehicle Name', max_length=100)
    colour = models.CharField(verbose_name='Colour', max_length=50)
    model = models.CharField(verbose_name='Model', max_length=50)
    chassis_number = models.CharField(verbose_name='Chassis Number', max_length=100)
    # tracker = models.ForeignKey(GPSTracker, on_delete=models.SET_NULL, blank=True, null=True)
    tracker = models.OneToOneField(GPSTracker, on_delete=models.SET_NULL, null=True, blank=True)
    insurance = models.BooleanField(verbose_name='Insurance', default=False)
    puc = models.BooleanField(verbose_name='PUC', default=False)
    seating_capacity = models.CharField(verbose_name='Seating Capacity', max_length=2)
    fuel_type = models.CharField(verbose_name='Fuel Type', max_length=100)
    air_condition = models.BooleanField(verbose_name='Air Condition', default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    class Meta:
        db_table = 'car'

    def __str__(self):
        return self.registration_number

class Zone(models.Model):
    zone_name = models.CharField(verbose_name='Zone Name', max_length=100)

    class Meta:
        db_table = 'zone'

    def __str__(self):
        return self.zone_name


class Tracker_data(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, default=1)
    zone = models.CharField(verbose_name='Zone', max_length=30)
    # zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name='Zone', max_length=30)
    vendor = models.CharField(verbose_name='Vendor', max_length=200)
    auth_key = models.CharField(verbose_name='Authentication Key', max_length=200)
    latitude = models.FloatField(verbose_name='Latitude', max_length=10)
    longitude = models.FloatField(verbose_name='Longitude', max_length=10)
    speed = models.FloatField(verbose_name='Speed', max_length=10)
    accuracy = models.FloatField(verbose_name='Accuracy', max_length=10)
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now=True)
    panic = models.BooleanField(verbose_name='Panic', default=0)
    ignition = models.BooleanField(verbose_name='Ignition', default=0)
    air_condition = models.CharField(verbose_name='Air Condition', max_length=10)
    # fleet_owner = models.ForeignKey(FleetOwner, on_delete=models.CASCADE, blank=True, default='')
    status = models.CharField(max_length=2, default='01')  # Status field
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'tracker_data'

    def __str__(self):
        return self.vendor


class RFID(models.Model):
    rfid_code = models.CharField(verbose_name='RFID Code', max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Is Active', default=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=1)  # Track who added the rfid

    class Meta:
        db_table = 'rfid'

    def __str__(self):
        return self.rfid_code


class Driver(models.Model):
    driver_name = models.CharField(verbose_name='Driver Name', max_length=200)
    driver_licence_number = models.CharField(verbose_name='Driver Licence Number', max_length=20)
    issue_date = models.DateField(verbose_name='Issue Date')
    valid_till = models.DateField(verbose_name='Valid Till')
    address = models.TextField(verbose_name='Address')
    upload_licence = models.ImageField(verbose_name='Upload Licence', upload_to='licence_uploads/')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rfid = models.OneToOneField(RFID, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='RFID')

    class Meta:
        db_table = 'driver'

    def __str__(self):
        return self.driver_name


class FleetOwnerSupport(models.Model):
    fleetowner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fleetowner')
    fleetowner_support_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fleetowner_support_person')

    class Meta:
        db_table = 'fleetowner_support'
    def __str__(self):
        return f"{self.fleetowner}'s FleetOwner Support Person: {self.fleetowner_support_user}"