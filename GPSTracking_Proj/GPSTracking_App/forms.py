from django import forms
from django.forms import ModelForm
from .models import Car, GPSTracker, Driver, RFID, Profile, FleetOwnerSupport
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class CarForm(forms.ModelForm):
    # tracker = forms.CharField(required=False, max_length=255, label="Tracker Serial Number")
    class Meta:
        model = Car
        fields = ['registration_number', 'registration_date', 'vehicle_name', 'colour', 'model', 'chassis_number', 'tracker', 'insurance', 'puc', 'seating_capacity', 'fuel_type', 'air_condition']
        widgets = {
            'registration_number': forms.TextInput(attrs={'placeholder': 'Enter car number', 'class': 'form-control'}),
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'vehicle_name': forms.TextInput(attrs={'placeholder': 'Enter car name', 'class': 'form-control'}),
            'colour': forms.TextInput(attrs={'placeholder': 'Enter colour', 'class': 'form-control'}),
            'model': forms.TextInput(attrs={'placeholder': 'Enter Model', 'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'placeholder': 'Enter Chassis Number', 'class': 'form-control'}),
            'seating_capacity': forms.TextInput(attrs={'placeholder': 'Enter Seating Capacity', 'class': 'form-control'}),
            'fuel_type': forms.TextInput(attrs={'placeholder': 'Enter Fuel Type', 'class': 'form-control'}),
            'tracker': forms.Select(attrs={'class': 'form-select'}),  # Use Select for dropdown
        }

        # def clean_tracker_serial_number(self):
        #     tracker_serial_number = self.cleaned_data.get('tracker')
        #     if tracker_serial_number:
        #         try:
        #             tracker = GPSTracker.objects.get(serial_number=tracker_serial_number)
        #             return tracker
        #         except GPSTracker.DoesNotExist:
        #             raise forms.ValidationError("Tracker with this serial number does not exist.")
        #     return None

        # def __init__(self, *args, **kwargs):
        #     super(CarForm, self).__init__(*args, **kwargs)
        #     # Populate the tracker dropdown with available GPSTrackers
        #     self.fields['tracker'].queryset = GPSTracker.objects.all()
        #     self.fields['tracker'].empty_label = "Select a tracker"

class TrackerForm(forms.ModelForm):
    class Meta:
        model = GPSTracker
        fields = ['serial_number']
        exclude = ['added_by']
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['driver_name', 'driver_licence_number', 'issue_date', 'valid_till', 'address', 'upload_licence', 'car', 'rfid']
        widgets = {
            'driver_name': forms.TextInput(attrs={'placeholder': 'Enter Driver Name', 'class': 'form-control'}),
            'driver_licence_number': forms.TextInput(attrs={'placeholder': 'Enter Driver Licence Number', 'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': "form-control"}),
            'valid_till': forms.DateInput(attrs={'type': 'date', 'class': "form-control"}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter Address', 'class': 'form-control', 'rows': 5}),
            'upload_licence': forms.FileInput(attrs={'class': 'form-control'}),
            'car': forms.Select(attrs={'class': 'form-select'}),
            'rfid': forms.Select(attrs={'class': 'form-select'})

        }

class RFIDForm(forms.ModelForm):
    class Meta:
        model = RFID
        fields = ['rfid_code', 'is_active']
        widgets = {
            'rfid_code': forms.TextInput(attrs={'placeholder': 'Enter RFID Number', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }


class UserRegisterForm(UserCreationForm):
    # address1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    # address2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    # city = forms.CharField(max_length=255, required=True, label="City")
    # state = forms.CharField(max_length=255, required=True, label="State")
    # pin = forms.CharField(max_length=6, required=True, label="Pin")
    # country = forms.CharField(max_length=255, required=True, label="Country")
    # mobile = forms.CharField(max_length=15, required=True, label='Mobile/Whatsapp Number')

    class Meta:
        model = User
        # fields = ['first_name', 'last_name', 'username', 'email', 'contact_number', 'address', 'aadhar_number', 'pan_number', 'resident_proof']
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    # Ensure that first_name and last_name are required
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        # Optionally, you can add custom error messages:
    # def clean_first_name(self):
    #     first_name = self.cleaned_data.get('first_name')
    #     if not first_name:
    #         raise forms.ValidationError('This field is required.')
    #     return first_name
    #
    # def clean_last_name(self):
    #     last_name = self.cleaned_data.get('last_name')
    #     if not last_name:
    #         raise forms.ValidationError('This field is required.')
    #     return last_name
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save profile data
            Profile.objects.create(
                user=user,
                address1=self.cleaned_data['address1'],
                address2=self.cleaned_data['address2'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                pin=self.cleaned_data['pin'],
                country=self.cleaned_data['country'],
                mobile=self.cleaned_data['mobile']
            )
        return user


# class LoginForm(forms.ModelForm):
#     remember_me = forms.BooleanField(required=False)  # Add this field
#
#     class Meta:
#         model = User
#         fields = ['username', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)  # Add this field


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address1', 'address2', 'city', 'state', 'pin', 'country', 'mobile']


# class FleetOwnerSupportUserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email', 'username', 'password']
#
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     def __init__(self, *args, **kwargs):
#         super(FleetOwnerSupportUserForm, self).__init__(*args, **kwargs)
#         self.fields['first_name'].required = True
#         self.fields['last_name'].required = True
#         self.fields['email'].required = True
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])
#         if commit:
#             user.save()
#             # Add user to 'fleetowner support' group
#             fleetowner_support_group = Group.objects.get(name='fleetowner_support_person')
#             user.groups.add(fleetowner_support_group)
#         return user


class FleetOwnerSupportUserForm(forms.ModelForm):
    address1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    address2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    city = forms.CharField(max_length=255, required=True, label="City")
    state = forms.CharField(max_length=255, required=True, label="State")
    pin = forms.CharField(max_length=6, required=True, label="Pin")
    country = forms.CharField(max_length=255, required=True, label="Country")
    mobile = forms.CharField(max_length=15, required=True, label='Mobile/Whatsapp Number')
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    password = forms.CharField(widget=forms.PasswordInput)

    def save(self, fleetowner, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Add user to 'fleetowner support' group
            fleetowner_support_group = Group.objects.get(name='fleetowner_support_person')
            user.groups.add(fleetowner_support_group)

            # Create FleetOwnerSupport entry to link the support user with the fleetowner
            FleetOwnerSupport.objects.create(fleetowner=fleetowner, fleetowner_support_user=user)
        return user

