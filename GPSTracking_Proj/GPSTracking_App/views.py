from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import FleetOwnerForm, CarForm, TrackerForm, DriverForm, RFIDForm
from .models import FleetOwner, Tracker_data, Car, GPSTracker, Driver, RFID


# Create your views here.
# from login_required import login_not_required


# - Login
# @login_not_required
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('dashboard')  # Update with your dashboard URL name
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# - Sign Up
# @login_not_required
def signup(request):
    return render(request, 'sign_up.html')


# - Add Fleet Owner
def add_fleet_owner(request):
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('fleet_owner_list')  # Redirect to a view that displays the list of fleet owners
    else:
        form = FleetOwnerForm()

    return render(request, 'add_fleet_owner.html', {'form': form})


# - Fleet Owner List
def fleet_owner_list(request):
    fleetowners = FleetOwner.objects.all()
    return render(request, 'fleet_owner_list.html', context={'fleetowners': fleetowners})

# - Update FleetOwner
def update_fleetowner(request, id):
    fleetowner = get_object_or_404(FleetOwner, pk=id)
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, instance=fleetowner)
        if form.is_valid():
            form.save()
            return redirect('fleet_owner_list')  # Adjust the URL name based on your setup
    else:
        form = FleetOwnerForm(instance=fleetowner)
    return render(request, 'update_fleetowner.html', {'form': form, 'fleetowner': fleetowner})
# - Tracker Data
# @login_required
# def tracker_data(request):
#     # Assuming the query string is in the request.GET dictionary
#     car = str(request.GET.get('car', Car))
#     zone = str(request.GET.get('zone', 0))
#     vendor = str(request.GET.get('vendor', 0))
#     auth_key = str(request.GET.get('auth_key', 0))
#     latitude = float(request.GET.get('latitude', 0))
#     longitude = float(request.GET.get('longitude', 0))
#     speed = float(request.GET.get('speed', 0))
#     accuracy = float(request.GET.get('accuracy', 0))
#     timestamp = str(request.GET.get('timestamp', 0))
#     panic = bool(request.GET.get('panic', 0))
#     ignition = bool(request.GET.get('ignition', 0))
#     air_condition = str(request.GET.get('air_condition', 0))
#     # Create a new Tracker_data instance and save it to the database
#     tracker_data_list = Tracker_data.objects.create(car=car, zone=zone, vendor=vendor, auth_key=auth_key,
#                                                     latitude=latitude, longitude=longitude, speed=speed,
#                                                     accuracy=accuracy, timestamp=timestamp, panic=panic,
#                                                     ignition=ignition, air_condition=air_condition)
#     tracker_data_list.save()
#     tracker_data_list = Tracker_data.objects.all()
#     return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list})

# @login_required
def tracker_data(request):
    tracker_data_list = Tracker_data.objects.all()
    total_count = Tracker_data.objects.count()  # Get the total count of rows
    # Get count of active cars
    # active_count = Tracker_data.objects.filter(status='active').count()

    # Get count of inactive cars
    # inactive_count = Tracker_data.objects.filter(status='inactive').count()

    return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})


def tracker_data1(request):
    tracker_data_list = Tracker_data.objects.all()
    return render(request, 'dashboard1.html', context={'tracker_data_list': tracker_data_list})

# - Add Car
# def add_car(request):
#     if request.method == 'POST':
#         form = CarForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('car_list')  # Redirect to a view that displays the list of cars
#     else:
#         form = CarForm()
#
#     return render(request, 'add_car.html', {'form': form})

def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)

            # Check if a tracker with the provided serial number exists
            tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
            if tracker_serial_number:
                tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
                car.tracker = tracker

            car.save()
            return redirect('car_list')  # Adjust the URL name based on your setup
    else:
        form = CarForm()

    return render(request, 'add_car.html', {'form': form})


# - Car List
def car_list(request):
    car_list = Car.objects.all()
    return render(request, 'car_list.html', context={'car_list': car_list})

# Update Car
def update_car(request, id):
    car = get_object_or_404(Car, pk=id)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_list')  # Adjust the URL name based on your setup
    else:
        form = CarForm(instance=car)
    return render(request, 'update_car.html', {'form': form, 'car': car})
# - Add Driver
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})

def driver_list(request):
    drivers_list = Driver.objects.all()
    return render(request, 'driver_list.html', context={'drivers_list': drivers_list})

def update_driver(request, id):
    driver = get_object_or_404(Driver, pk=id)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('driver_list')  # Adjust the URL name based on your setup
    else:
        form = DriverForm(instance=driver)
    return render(request, 'update_driver.html', {'form': form, 'driver': driver})


def delete_driver(request, id):
    driver = get_object_or_404(Driver, id=id)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')  # Replace with your actual driver list URL name

    return render(request, 'delete_driver.html', {'driver': driver})



# - Add Tracker
def add_tracker(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker_list')
    else:
        form = TrackerForm()
    return render(request, 'add_tracker.html', {'form': form})



# - Tracker List
def tracker_list(request):
    tracker_list = GPSTracker.objects.all()
    return render(request, 'tracker_list.html', {'tracker_list': tracker_list})


# - Add RFID
def add_rfid(request):
    if request.method == 'POST':
        form = RFIDForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rfid_list')  # Redirect to a view that displays the list of RFIDs
    else:
        form = RFIDForm()

    return render(request, 'add_rfid.html', {'form': form})

# - RFID List
def rfid_list(request):
    rfid_list = RFID.objects.all()
    return render(request, 'rfid_list.html', {'rfid_list': rfid_list})


def update_rfid(request, id):
    rfid = get_object_or_404(RFID, pk=id)
    if request.method == 'POST':
        form = RFIDForm(request.POST, instance=rfid)
        if form.is_valid():
            form.save()
            return redirect('rfid_list')  # Adjust the URL name based on your setup
    else:
        form = RFIDForm(instance=rfid)
    return render(request, 'update_rfid.html', {'form': form, 'rfid': rfid})


def delete_rfid(request, id):
    rfid = get_object_or_404(RFID, id=id)
    if request.method == 'POST':
        rfid.delete()
        return redirect('rfid_list')  # Replace with your actual driver list URL name

    return render(request, 'delete_rfid.html', {'rfid': rfid})
