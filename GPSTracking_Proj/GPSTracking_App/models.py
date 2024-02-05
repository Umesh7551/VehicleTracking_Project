# from django.contrib.gis.geos import Point, LineString
from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Create your models here.


# class FleetOwner(AbstractUser):
#     name = models.CharField(verbose_name='Name', max_length=200)
#     email = models.EmailField(verbose_name='Email Address', max_length=100, unique=True)
#     password = models.CharField(verbose_name='Password', max_length=200, blank=True)
#     confirm_password = models.CharField(verbose_name='Confirm Password', max_length=200, blank=True)
#     contact_number = models.CharField(verbose_name='Contact Number', max_length=10)
#     address = models.TextField(verbose_name='Address', max_length=200)
#     aadhar_number = models.CharField(verbose_name='Aadhar Number', max_length=12, unique=True)
#     pan_number = models.CharField(verbose_name='PAN Number', max_length=10, unique=True)
#     resident_proof = models.ImageField(verbose_name='Resident Proof', upload_to='fleetowner_uploads/')
#
#     class Meta:
#         db_table = 'fleetowner'
#
#     def __str__(self):
#         return self.name

class FleetOwner(models.Model):
    name = models.CharField(verbose_name='Name', max_length=200)
    email = models.EmailField(verbose_name='Email Address', max_length=100, unique=True)
    password = models.CharField(verbose_name='Password', max_length=200, blank=True)
    confirm_password = models.CharField(verbose_name='Confirm Password', max_length=200, blank=True)
    contact_number = models.CharField(verbose_name='Contact Number', max_length=10)
    address = models.TextField(verbose_name='Address', max_length=200)
    aadhar_number = models.CharField(verbose_name='Aadhar Number', max_length=12, unique=True)
    pan_number = models.CharField(verbose_name='PAN Number', max_length=10, unique=True)
    resident_proof = models.ImageField(verbose_name='Resident Proof', upload_to='fleetowner_uploads/')

    class Meta:
        db_table = 'fleetowner'

    def __str__(self):
        return self.name


class GPSTracker(models.Model):
    serial_number = models.CharField(verbose_name='Serial Number', max_length=200, unique=True)
    # car = models.OneToOneField(Car, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gpstracker'

    def __str__(self):
        return self.serial_number


class Car(models.Model):
    registration_number = models.CharField(verbose_name='Registration Number', max_length=20, unique=True)
    registration_date = models.DateField(verbose_name='Registration Date')
    vehicle_name = models.CharField(verbose_name='Vehicle Name', max_length=100)
    colour = models.CharField(verbose_name='Colour', max_length=50)
    model = models.CharField(verbose_name='Model', max_length=50)
    chassis_number = models.CharField(verbose_name='Chassis Number', max_length=100, unique=True)
    # tracker_id = models.CharField(verbose_name='Tracker ID', max_length=20, unique=True)
    tracker_id = models.ForeignKey(GPSTracker, on_delete=models.SET_NULL, blank=True, null=True)
    insurance = models.BooleanField(verbose_name='Insurance', default=1)
    puc = models.BooleanField(verbose_name='PUC', default=1)
    seating_capacity = models.CharField(verbose_name='Seating Capacity', max_length=2)
    fuel_type = models.CharField(verbose_name='Fuel Type', max_length=100)
    air_condition = models.BooleanField(verbose_name='Air Condition', default=1)
    owner = models.ForeignKey(FleetOwner, on_delete=models.CASCADE)

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
    ignition = models.BooleanField(verbose_name='Ignition', default=1)
    air_condition = models.CharField(verbose_name='Air Condition', max_length=10)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'tracker_data'

    def __str__(self):
        return self.vendor


class RFID(models.Model):
    rfid_code = models.CharField(verbose_name='RFID Code', max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Is Active', default=True)

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


