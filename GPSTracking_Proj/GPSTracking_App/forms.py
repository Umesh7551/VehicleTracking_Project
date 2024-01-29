from django import forms
from .models import FleetOwner, Car, GPSTracker, Driver, RFID
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
class FleetOwnerForm(forms.ModelForm):
    class Meta:
        model = FleetOwner
        fields = ['name', 'email', 'password', 'confirm_password', 'contact_number', 'address', 'aadhar_number', 'pan_number', 'resident_proof']



class CarForm(forms.ModelForm):
    # Define a new field for the tracker serial number
    # tracker_serial_number = forms.CharField(label='Tracker Serial Number', required=False)

    class Meta:
        model = Car
        fields = ['registration_number', 'registration_date', 'vehicle_name', 'colour', 'model', 'chassis_number', 'tracker_id', 'insurance', 'puc', 'seating_capacity', 'fuel_type', 'air_condition', 'owner']

    # def __init__(self, *args, **kwargs):
    #     super(CarForm, self).__init__(*args, **kwargs)
    #
    #     # Update the widget for the tracker serial number field if needed
    #     self.fields['tracker_serial_number'].widget.attrs.update({'placeholder': 'Enter tracker serial number'})


class TrackerForm(forms.ModelForm):
    class Meta:
        model = GPSTracker
        fields = ['serial_number']

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['driver_name', 'driver_licence_number', 'issue_date', 'valid_till', 'address', 'upload_licence', 'car', 'rfid']


class RFIDForm(forms.ModelForm):
    class Meta:
        model = RFID
        fields = ['rfid_code', 'is_active']
