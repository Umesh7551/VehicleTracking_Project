from django import forms
from django.forms import ModelForm
from .models import Car, GPSTracker, Driver, RFID, Profile, FleetOwnerSupport
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['registration_number', 'registration_date', 'vehicle_name', 'colour', 'model', 'chassis_number', 'tracker', 'insurance', 'puc', 'seating_capacity', 'fuel_type', 'air_condition']
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
        }

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


class UserRegisterForm(UserCreationForm):
    address1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    address2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    city = forms.CharField(max_length=255, required=True, label="City")
    state = forms.CharField(max_length=255, required=True, label="State")
    pin = forms.CharField(max_length=6, required=True, label="Pin")
    country = forms.CharField(max_length=255, required=True, label="Country")
    mobile = forms.CharField(max_length=15, required=True, label='Mobile/Whatsapp Number')

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


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

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

